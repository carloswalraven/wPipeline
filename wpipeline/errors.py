"""Exception hierarchy for the wpipeline package.

Nothing in this package calls sys.exit() or writes to stderr. Every failure
leaves through one of these exceptions, and the CLI layer decides how to show
it and which exit code to use.

The reason is not style. A library that runs inside Houdini cannot kill the
artist's session with a SystemExit. die() is correct in launch_houdini.py,
which is a terminal script where exiting is the point, and wrong here.

Every exception carries a message that is already readable by a human: the CLI
prints it as-is, so the wording lives next to the code that knows what failed.
"""


class WPipelineError(Exception):
    """Base class for every error this package raises.

    The CLI catches this one, which means a new subclass is reportable the day
    it is written, without touching the CLI.
    """


class PolicyError(WPipelineError):
    """The versioned pipeline policy is missing or malformed.

    This one means the repo itself is broken, not the machine: the policy ships
    with the package.
    """


class ConfigError(WPipelineError):
    """The machine configuration is unreadable, or declares no roots."""


class ValidationError(WPipelineError):
    """A user supplied value breaks a sealed grammar rule."""


class RootError(WPipelineError):
    """A declared production root cannot be used right now.

    Covers both an unmounted volume and a path that does not exist, because
    both mean the same thing to the caller: that root cannot be read today.
    The message tells the two apart, since the fixes are different.
    """


class SourceOfTruthError(WPipelineError):
    """The source of truth cannot answer with the certainty the caller needs."""


class ProjectExistsError(SourceOfTruthError):
    """The project code is already taken, in this root or in another one.

    Uniqueness is global across every root, so this is not a per-root clash.
    """


class PathConflictError(SourceOfTruthError):
    """The target folder exists but holds no project file.

    The gatekeeper does not adopt what it did not write, so this is never
    repaired automatically.
    """


class CorruptProjectFileError(SourceOfTruthError):
    """A project.json exists but cannot be trusted.

    Invalid JSON, or one of the six sealed fields is missing. Reading tolerates
    this as a warning; writing does not, because the damaged file could be the
    very one declaring the code being requested.
    """


class HoudiniNotFoundError(WPipelineError):
    """No usable Houdini installation was found on this machine.

    Not fatal to project creation: the caller writes a null houdini_version and
    warns, because tying project creation to an installed DCC would break
    headless automation.
    """
