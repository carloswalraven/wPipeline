"""The two configuration layers, which have opposite rules.

Pipeline policy is what the tool *is*: the closed vocabularies, the grammar,
the padding. It is the same on every machine, it is versioned in the repo, and
it ships inside this package. An environment variable cannot replace it, or the
closed vocabulary would be open through the back door.

Machine configuration is where storage lives on *this* box: the named
production roots. It is local and stays out of git, because a Dropbox path in a
public repo is hardcoding that merely changed address.

Discovery for the machine layer, with no merging:

    WPIPELINE_CONFIG (a file)  ->  ~/.config/wpipeline/machine.json  ->  empty

The first layer that exists wins whole, and the result reports which one it came
from. Merging three layers is where "so where did this value come from?" bugs
are born, and answering that question costs more than inheriting half a file
saves.
"""

import json
import os
from pathlib import Path

from .errors import ConfigError, PolicyError

POLICY_PATH = Path(__file__).parent / "policy" / "pipeline.json"

MACHINE_ENV_VAR = "WPIPELINE_CONFIG"
MACHINE_CONFIG_PATH = Path.home() / ".config" / "wpipeline" / "machine.json"

SOURCE_ENVIRONMENT = "environment"
SOURCE_USER_FILE = "user file"
SOURCE_DEFAULTS = "defaults"

# Deliberately a placeholder volume. This string ships in a public repo, so it
# must never carry a real local path.
EXAMPLE_MACHINE_CONFIG = """{
  "schema_version": 1,
  "roots": {
    "main": "/Volumes/YourVolume/wPipeline_Projects"
  }
}"""


class MachineConfig:
    """The machine layer, plus the record of which layer answered.

    Knowing the source is not a nicety. When the tool reports no projects, the
    first question is always which configuration it actually read, and a tool
    that cannot answer it sends you reading its source code.
    """

    def __init__(self, roots, source, path=None):
        self.roots = roots
        self.source = source
        self.path = path

    @property
    def description(self):
        """One line naming the layer and the file, ready to print."""
        if self.source == SOURCE_ENVIRONMENT:
            return f"{MACHINE_ENV_VAR}={self.path}"
        if self.source == SOURCE_USER_FILE:
            return f"user file {self.path}"
        return "built-in defaults (no roots declared)"

    def root_names(self):
        """Declared root names, sorted, for messages that list the options."""
        return sorted(self.roots)


def load_policy(path=None):
    """Reads the versioned pipeline policy that ships with the package.

    Resolved relative to this file and never to the working directory: the tool
    has to answer the same from any folder, including from inside Houdini.
    """
    path = POLICY_PATH if path is None else Path(path)

    if not path.is_file():
        raise PolicyError(
            f"The pipeline policy is missing: {path}\n"
            "This file ships with the package, so its absence means a broken "
            "install rather than a machine that needs configuring."
        )

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"Cannot read the pipeline policy {path}: {exc}")

    try:
        return json.loads(text)
    except ValueError as exc:
        raise PolicyError(f"The pipeline policy {path} is not valid JSON: {exc}")


def load_machine_config(env=None, default_path=None):
    """Resolves the machine layer, first layer that exists winning whole.

    A WPIPELINE_CONFIG pointing at a file that does not exist is an error, not
    a reason to fall through to the next layer. Pointing at a missing file is a
    broken declaration, not an absent one, and falling through in silence would
    turn a typo in the variable into "all my projects disappeared".
    """
    env = os.environ if env is None else env
    default_path = MACHINE_CONFIG_PATH if default_path is None else Path(default_path)

    declared = env.get(MACHINE_ENV_VAR, "").strip()
    if declared:
        path = Path(declared).expanduser()
        if not path.is_file():
            raise ConfigError(
                f"{MACHINE_ENV_VAR} points at a file that does not exist:\n"
                f"  {path}\n"
                "Fix the variable or unset it to fall back to "
                f"{MACHINE_CONFIG_PATH}."
            )
        return _read_machine_file(path, SOURCE_ENVIRONMENT)

    if default_path.is_file():
        return _read_machine_file(default_path, SOURCE_USER_FILE)

    return MachineConfig(roots={}, source=SOURCE_DEFAULTS, path=None)


def _read_machine_file(path, source):
    """Parses one machine configuration file into a MachineConfig."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Cannot read the machine configuration {path}: {exc}")

    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ConfigError(
            f"The machine configuration {path} is not valid JSON: {exc}"
        )

    if not isinstance(data, dict):
        raise ConfigError(
            f"The machine configuration {path} must hold a JSON object."
        )

    if "roots" not in data:
        raise ConfigError(
            f"The machine configuration {path} declares no 'roots' key.\n"
            f"Expected shape:\n\n{EXAMPLE_MACHINE_CONFIG}"
        )

    raw_roots = data["roots"]
    if not isinstance(raw_roots, dict):
        raise ConfigError(
            f"In {path}, 'roots' must be an object mapping a logical name to a "
            "path, so that the name is unique without validating it apart."
        )

    roots = {}
    for name, value in raw_roots.items():
        if not isinstance(value, str) or not value.strip():
            raise ConfigError(
                f"In {path}, root '{name}' must be a non-empty path string."
            )
        # expanduser so that a config file can say ~ and stay portable across
        # user names, the same reason the launcher uses $HOME.
        roots[name] = Path(value).expanduser()

    return MachineConfig(roots=roots, source=source, path=path)


def require_roots(config):
    """Returns the declared roots, or raises with instructions.

    Zero roots is the first thing that happens to anyone who clones the repo on
    a clean machine, so the message carries the exact file to write and content
    that can be copied off the screen. A tool that says "no roots" without
    saying how roots are declared forces you to guess or to read its source.
    """
    if config.roots:
        return config.roots

    raise ConfigError(
        "No production roots are declared, so there is nowhere to work.\n"
        f"Configuration read from: {config.description}\n\n"
        f"Create this file:\n  {MACHINE_CONFIG_PATH}\n\n"
        f"With content like:\n\n{EXAMPLE_MACHINE_CONFIG}\n\n"
        f"Roots are machine configuration and stay out of git. Set "
        f"{MACHINE_ENV_VAR} to use a different file."
    )
