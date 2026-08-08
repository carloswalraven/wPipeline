"""Houdini discovery, under the package's exception contract.

parse_version is copied verbatim from launch_houdini.py. It is pure, it never
touches disk, and stage 0 already proved it against a synthetic list of folder
names. Copying a proven pure function is cheaper than sharing it across a
boundary that stage 1b is going to move anyway.

find_newest_houdini is rewritten rather than copied, because its only real
difference is how it fails: die() there, raise here. Same logic, different
contract, and the contract is the whole point.

Debt, already noted in PENDIENTES.md: two copies of this live in the repo until
stage 1b migrates launch_houdini.py. That day the script's copies go and these
stay as the only ones.
"""

import re
from pathlib import Path

from .errors import HoudiniNotFoundError

HOUDINI_APPS_DIR = Path("/Applications/Houdini")
VERSION_RE = re.compile(r"^Houdini(\d+)\.(\d+)\.(\d+)$")


def parse_version(name):
    """'Houdini21.0.671' -> (21, 0, 671). None if the name is not a version."""
    match = VERSION_RE.match(name)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def format_version(version):
    """(21, 0, 671) -> '21.0.671'.

    This is the form written to project.json: it is what a human reads on the
    folder name and what a human would type. The tuple is an internal detail
    that exists so that versions sort as numbers and not as text.
    """
    return ".".join(str(part) for part in version)


def find_newest_houdini(apps_dir=None):
    """Returns (version_tuple, folder) for the newest installed version.

    Sorting is done on the numeric tuple, never on the string: as text,
    '21.0.671' would beat '21.0.1000'.

    Raises HoudiniNotFoundError when the applications folder is missing or
    holds no recognizable version. The caller decides whether that is fatal;
    for project creation it is not.
    """
    apps_dir = HOUDINI_APPS_DIR if apps_dir is None else Path(apps_dir)

    if not apps_dir.is_dir():
        raise HoudiniNotFoundError(
            f"{apps_dir} does not exist. Houdini does not seem installed."
        )

    found = []
    for entry in apps_dir.iterdir():
        version = parse_version(entry.name)
        if version is not None:
            found.append((version, entry))

    if not found:
        raise HoudiniNotFoundError(f"Found no Houdini version in {apps_dir}.")

    found.sort()
    return found[-1]
