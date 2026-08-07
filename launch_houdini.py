#!/usr/bin/env python3
"""wPipeline - Stage 0.

Launches Houdini Apprentice with HOUDINI_OTLSCAN_PATH pointing at an external
folder, preserving Houdini's own default paths with the '&' separator. Tests a
single assumption: that the external HDA shows up in the tab menu.
"""

import os
import re
import sys
from pathlib import Path

HOUDINI_APPS_DIR = Path("/Applications/Houdini")
HDA_DIR = Path(
    "/Volumes/W_AirProjects/Dropbox/APPS/wPipeline_Projects/_etapa0_test/publish/hda"
)
HDA_EXTENSIONS = (".hda", ".hdalc", ".hdanc")
VERSION_RE = re.compile(r"^Houdini(\d+)\.(\d+)\.(\d+)$")


def die(message):
    """Exits with a readable message. Never a traceback."""
    print(f"\nERROR: {message}\n", file=sys.stderr)
    sys.exit(1)


def parse_version(name):
    """'Houdini21.0.671' -> (21, 0, 671). None if the name is not a version."""
    match = VERSION_RE.match(name)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def find_newest_houdini():
    """Returns (version, folder) for the newest installed version."""
    if not HOUDINI_APPS_DIR.is_dir():
        die(f"{HOUDINI_APPS_DIR} does not exist. Houdini does not seem installed.")

    found = []
    for entry in HOUDINI_APPS_DIR.iterdir():
        version = parse_version(entry.name)
        if version is not None:
            found.append((version, entry))

    if not found:
        die(f"Found no Houdini version in {HOUDINI_APPS_DIR}.")

    found.sort()
    return found[-1]


def find_apprentice(version_dir):
    """Returns the real Houdini Apprentice binary inside the .app bundle."""
    bundles = sorted(version_dir.glob("Houdini Apprentice *.app"))
    if not bundles:
        die(f"Found no 'Houdini Apprentice *.app' inside {version_dir}.")

    binary = bundles[-1] / "Contents" / "MacOS" / "happrentice"
    if not binary.is_file():
        die(f"The bundle exists but the executable is missing:\n  {binary}")
    if not os.access(binary, os.X_OK):
        die(f"The executable exists but has no execute permission:\n  {binary}")
    return binary


def volume_root(path):
    """For /Volumes/X/... returns /Volumes/X. None if not on a volume."""
    parts = path.parts
    if len(parts) >= 3 and parts[1] == "Volumes":
        return Path(*parts[:3])
    return None


def check_hda_dir():
    """Validates the test folder and returns the HDAs it contains."""
    volume = volume_root(HDA_DIR)
    if volume is not None and not volume.is_dir():
        die(
            f"Volume {volume} is not mounted.\n"
            f"       Connect it and try again."
        )
    if not HDA_DIR.exists():
        die(f"The test folder does not exist:\n         {HDA_DIR}")
    if not HDA_DIR.is_dir():
        die(f"It exists but is not a folder:\n         {HDA_DIR}")

    return sorted(
        entry
        for entry in HDA_DIR.iterdir()
        if entry.is_file() and entry.suffix.lower() in HDA_EXTENSIONS
    )


def main():
    version, version_dir = find_newest_houdini()
    binary = find_apprentice(version_dir)
    hdas = check_hda_dir()
    otlscan_path = f"{HDA_DIR}:&"

    print(f"Houdini     : {'.'.join(str(n) for n in version)}")
    print(f"Executable  : {binary}")
    print(f"HDA folder  : {HDA_DIR}")
    print(f"OTLSCAN     : {otlscan_path}")
    print("")

    if hdas:
        print(f"HDAs found ({len(hdas)}):")
        for entry in hdas:
            size = entry.stat().st_size
            flag = "  <-- 0 bytes, check Dropbox" if size == 0 else ""
            print(f"  {size:>12,} bytes  {entry.name}{flag}")
    else:
        print("WARNING: the folder has no HDAs yet. Launching anyway.")
    print("")

    print("Launching Houdini Apprentice...")
    env = os.environ.copy()
    env["HOUDINI_OTLSCAN_PATH"] = otlscan_path
    os.execve(str(binary), [str(binary)], env)


if __name__ == "__main__":
    main()
