"""What the source of truth hands back.

A ProjectRecord carries the six sealed fields of project.json plus two derived
values that are never written: the logical name of the root where the scan
found it, and the path, computed as configured root + code.

The path being computed rather than stored is the mechanical guarantee, not the
promise, that it cannot go stale: what is not saved cannot fall out of date.
The day the volume is renamed or mounted somewhere else, an immutable file that
had recorded an absolute path would be wrong, and this one simply is not.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..errors import CorruptProjectFileError

SCHEMA_VERSION = 1

# The six sealed fields, in the order they are written. Anything outside this
# tuple is derived and must never reach disk.
FILE_FIELDS = (
    "schema_version",
    "code",
    "name",
    "root",
    "houdini_version",
    "created",
)


@dataclass
class ProjectRecord:
    """One project, as the source of truth describes it."""

    schema_version: int
    code: str
    name: str
    root: str
    houdini_version: Optional[str]
    created: str

    # Derived. Never persisted.
    found_in_root: Optional[str] = None
    path: Optional[Path] = None

    @classmethod
    def from_file_data(cls, data, found_in_root, path, source_path):
        """Builds a record from parsed project.json content.

        Raises CorruptProjectFileError when a sealed field is missing. A file
        short of a field was a project once and something damaged it, which is
        a different thing from a folder that never was one.
        """
        if not isinstance(data, dict):
            raise CorruptProjectFileError(
                f"{source_path} does not hold a JSON object."
            )

        missing = [field for field in FILE_FIELDS if field not in data]
        if missing:
            raise CorruptProjectFileError(
                f"{source_path} is missing required "
                f"{'fields' if len(missing) > 1 else 'field'}: "
                f"{', '.join(missing)}."
            )

        return cls(
            schema_version=data["schema_version"],
            code=data["code"],
            name=data["name"],
            root=data["root"],
            houdini_version=data["houdini_version"],
            created=data["created"],
            found_in_root=found_in_root,
            path=path,
        )

    def to_file_data(self):
        """The dict written to project.json: exactly the six sealed fields.

        Built by hand rather than from the dataclass, so that adding a derived
        attribute can never leak one onto disk by accident.
        """
        return {
            "schema_version": self.schema_version,
            "code": self.code,
            "name": self.name,
            "root": self.root,
            "houdini_version": self.houdini_version,
            "created": self.created,
        }

    @property
    def root_matches_location(self):
        """True when the declared root is the one the scan actually read.

        Verifiable precisely because root holds a logical name: the tool found
        the file under some root and can confirm the field agrees.
        """
        if self.found_in_root is None:
            return True
        return self.root == self.found_in_root


@dataclass
class ScanResult:
    """The answer to "what projects exist", warts included.

    Reading tolerates a partial view, so this carries both what was found and
    what could not be read. An incomplete answer labelled as incomplete is
    still useful; refusing to answer helps nobody.

    Two kinds of trouble are kept apart on purpose, because only one of them
    blocks writing:

    - unreadable_roots and damaged_files hide codes from view, so uniqueness
      cannot be guaranteed and create-project must refuse.
    - inconsistencies are things that read fine and merely disagree, such as a
      project whose root field is not the root it was found in. Its code is
      known, so uniqueness still holds and writing may proceed.

    Everything lands in warnings as well, because the user should see all of it
    either way.
    """

    projects: list
    warnings: list
    unreadable_roots: list
    damaged_files: list

    @property
    def partial(self):
        """True when at least one declared root could not be read."""
        return bool(self.unreadable_roots)

    @property
    def has_damage(self):
        """True when something is hidden from view.

        This is the flag writing consults: create-project needs certainty, and
        certainty is absent whether a whole root is missing or a single project
        file cannot be parsed.
        """
        return bool(self.unreadable_roots) or bool(self.damaged_files)
