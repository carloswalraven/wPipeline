#!/usr/bin/env python3
"""wPipeline - Etapa 0.

Lanza Houdini Apprentice con HOUDINI_OTLSCAN_PATH apuntando a una carpeta
externa, preservando las rutas por defecto de Houdini con el separador '&'.
Prueba un solo supuesto: que el HDA externo aparezca en el tab menu.
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
    """Corta con un mensaje legible. Nunca un traceback."""
    print(f"\nERROR: {message}\n", file=sys.stderr)
    sys.exit(1)


def parse_version(name):
    """'Houdini21.0.671' -> (21, 0, 671). None si no es una version."""
    match = VERSION_RE.match(name)
    if match is None:
        return None
    return tuple(int(part) for part in match.groups())


def find_newest_houdini():
    """Devuelve (version, carpeta) de la version mas reciente instalada."""
    if not HOUDINI_APPS_DIR.is_dir():
        die(f"No existe {HOUDINI_APPS_DIR}. Houdini no parece estar instalado.")

    found = []
    for entry in HOUDINI_APPS_DIR.iterdir():
        version = parse_version(entry.name)
        if version is not None:
            found.append((version, entry))

    if not found:
        die(f"No encontre ninguna version de Houdini en {HOUDINI_APPS_DIR}.")

    found.sort()
    return found[-1]


def find_apprentice(version_dir):
    """Devuelve el binario real de Houdini Apprentice dentro del bundle .app."""
    bundles = sorted(version_dir.glob("Houdini Apprentice *.app"))
    if not bundles:
        die(f"No encontre 'Houdini Apprentice *.app' dentro de {version_dir}.")

    binary = bundles[-1] / "Contents" / "MacOS" / "happrentice"
    if not binary.is_file():
        die(f"El bundle existe pero falta el ejecutable:\n  {binary}")
    if not os.access(binary, os.X_OK):
        die(f"El ejecutable existe pero no tiene permiso de ejecucion:\n  {binary}")
    return binary


def volume_root(path):
    """Para /Volumes/X/... devuelve /Volumes/X. None si no es un volumen."""
    parts = path.parts
    if len(parts) >= 3 and parts[1] == "Volumes":
        return Path(*parts[:3])
    return None


def check_hda_dir():
    """Valida la carpeta de prueba y devuelve los HDAs que contiene."""
    volume = volume_root(HDA_DIR)
    if volume is not None and not volume.is_dir():
        die(
            f"El volumen {volume} no esta montado.\n"
            f"       Conectalo y volve a intentar."
        )
    if not HDA_DIR.exists():
        die(f"No existe la carpeta de prueba:\n         {HDA_DIR}")
    if not HDA_DIR.is_dir():
        die(f"Existe pero no es una carpeta:\n         {HDA_DIR}")

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
    print(f"Ejecutable  : {binary}")
    print(f"Carpeta HDA : {HDA_DIR}")
    print(f"OTLSCAN     : {otlscan_path}")
    print("")

    if hdas:
        print(f"HDAs encontrados ({len(hdas)}):")
        for entry in hdas:
            size = entry.stat().st_size
            flag = "  <-- 0 bytes, revisar Dropbox" if size == 0 else ""
            print(f"  {size:>12,} bytes  {entry.name}{flag}")
    else:
        print("AVISO: la carpeta no tiene HDAs todavia. Lanzo igual.")
    print("")

    print("Lanzando Houdini Apprentice...")
    env = os.environ.copy()
    env["HOUDINI_OTLSCAN_PATH"] = otlscan_path
    os.execve(str(binary), [str(binary)], env)


if __name__ == "__main__":
    main()
