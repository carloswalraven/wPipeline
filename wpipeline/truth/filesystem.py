"""The source of truth backed by folders and project files.

Today this is what answers. Tomorrow it could be Flow or Kitsu, and nothing
that consumes the layer would change.

Two rules shape everything here.

One level per root. Projects are direct children of a root, so the scan looks
at first level folders and asks each one for a project file. Nothing recursive:
the main root lives in Dropbox, where a recursive sweep is slow and can touch
online-only files and force them down.

Reading tolerates a partial view; writing demands certainty. A missing volume
or an unparseable project file is a warning when listing and a refusal when
creating, because uniqueness of the project code is global across every root
and cannot be claimed over roots that were never read.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from ..errors import (
    CorruptProjectFileError,
    PathConflictError,
    ProjectExistsError,
    RootError,
    SourceOfTruthError,
)
from .base import SourceOfTruth
from .record import SCHEMA_VERSION, ProjectRecord, ScanResult

PROJECT_FILE = "project.json"

# The shape of a project: nothing else is created up front. Asset types and the
# dev sequence arrive in stage 1b, on the fly, when the first asset or shot
# does. These two go in because they are the form of the project itself.
PROJECT_FOLDERS = ("assets", "seq")


def volume_root(path):
    """For /Volumes/X/... returns /Volumes/X. None when not on a volume.

    Exists so that "the external disk is not connected" can be told apart from
    "the folder does not exist". Two problems, two different fixes.
    """
    parts = path.parts
    if len(parts) >= 3 and parts[1] == "Volumes":
        return Path(*parts[:3])
    return None


def describe_root_problem(root):
    """Returns why this root cannot be read now, or None when it can."""
    volume = volume_root(root)
    if volume is not None and not volume.is_dir():
        return f"volume {volume} is not mounted"
    if not root.exists():
        return f"{root} does not exist"
    if not root.is_dir():
        return f"{root} is not a folder"
    return None


def utc_timestamp():
    """Current time as an ISO 8601 string in UTC, to the second.

    Seconds are enough: microseconds are noise nobody will ever read, and the
    explicit +00:00 keeps the file unambiguous when it is read on a machine in
    another timezone.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class FilesystemSourceOfTruth(SourceOfTruth):
    """Answers by scanning the declared production roots."""

    def __init__(self, roots):
        """roots is a dict of logical name to Path, as configuration declares."""
        self.roots = dict(roots)

    # -- reading ---------------------------------------------------------

    def list_projects(self):
        """Scans every declared root, one level deep."""
        projects = []
        warnings = []
        unreadable_roots = []
        damaged_files = []

        for root_name in sorted(self.roots):
            root = self.roots[root_name]

            problem = describe_root_problem(root)
            if problem is not None:
                unreadable_roots.append(root_name)
                warnings.append(f"Root '{root_name}' cannot be read: {problem}.")
                continue

            for entry in sorted(root.iterdir()):
                if not entry.is_dir():
                    continue

                project_file = entry / PROJECT_FILE
                if not project_file.is_file():
                    # Ignored without noise. A folder with no project file was
                    # never a project, which is why this is not a warning.
                    continue

                try:
                    record = self._read_project(project_file, root_name, entry)
                except CorruptProjectFileError as exc:
                    damaged_files.append(str(project_file))
                    warnings.append(str(exc))
                    continue

                if not record.root_matches_location:
                    # Reads fine, merely disagrees. Reported, never repaired.
                    warnings.append(
                        f"Project '{record.code}' declares root "
                        f"'{record.root}' but was found in '{root_name}' "
                        f"({project_file})."
                    )

                projects.append(record)

        return ScanResult(
            projects=projects,
            warnings=warnings,
            unreadable_roots=unreadable_roots,
            damaged_files=damaged_files,
        )

    def get_project(self, code):
        """Returns the record for a code, or None.

        Derived from the scan here. Against a tracker it would be an indexed
        query, and the interface is what lets the backend choose.
        """
        for record in self.list_projects().projects:
            if record.code == code:
                return record
        return None

    def _read_project(self, project_file, root_name, folder):
        """Parses one project file into a record, or raises."""
        try:
            text = project_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise CorruptProjectFileError(f"Cannot read {project_file}: {exc}")

        try:
            data = json.loads(text)
        except ValueError as exc:
            raise CorruptProjectFileError(
                f"{project_file} is not valid JSON: {exc}"
            )

        return ProjectRecord.from_file_data(
            data,
            found_in_root=root_name,
            path=folder,
            source_path=project_file,
        )

    # -- writing ---------------------------------------------------------

    def create_project(self, code, name, root_name, houdini_version):
        """Creates the project folder, its project file and assets/ and seq/.

        Refuses, without touching disk, when the code is taken anywhere, when
        the target folder already exists, or when any root or project file
        could not be read.
        """
        if root_name not in self.roots:
            available = ", ".join(sorted(self.roots)) or "none"
            raise RootError(
                f"Unknown root '{root_name}'. Declared roots: {available}."
            )

        scan = self.list_projects()
        if scan.has_damage:
            raise SourceOfTruthError(
                "Cannot create a project without a complete view of every "
                "root, because the project code has to be unique across all "
                "of them.\n"
                + "\n".join(f"  - {line}" for line in scan.warnings)
            )

        for record in scan.projects:
            if record.code == code:
                raise ProjectExistsError(
                    f"Project code '{code}' already exists in root "
                    f"'{record.found_in_root}': {record.path}"
                )

        target = self.roots[root_name] / code
        if target.exists():
            raise PathConflictError(
                f"{target} already exists but holds no project file. Nothing "
                "was touched: the gatekeeper does not adopt what it did not "
                "write. Remove it by hand if it is leftover."
            )

        record = ProjectRecord(
            schema_version=SCHEMA_VERSION,
            code=code,
            name=name,
            root=root_name,
            houdini_version=houdini_version,
            created=utc_timestamp(),
            found_in_root=root_name,
            path=target,
        )

        target.mkdir()
        for folder in PROJECT_FOLDERS:
            (target / folder).mkdir()

        # The project file goes last on purpose. If anything above fails, what
        # is left behind has no project file, so the scan ignores it and the
        # code stays free. A half made project is removed by hand; that cost is
        # accepted and is cheaper than adopting a folder nobody wrote.
        project_file = target / PROJECT_FILE
        project_file.write_text(
            json.dumps(record.to_file_data(), indent=2) + "\n", encoding="utf-8"
        )

        return record
