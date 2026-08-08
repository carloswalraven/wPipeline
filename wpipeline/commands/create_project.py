"""Creating a project: the gatekeeper's first action.

The order is deliberate. Pure validation runs first, because it costs nothing
and fails clearest. Configuration comes next, then the root is resolved, then
Houdini is looked for, and only then does the source of truth get asked to
write. Nothing touches disk until every question with an answer has one.
"""

from dataclasses import dataclass, field

from .. import naming
from ..config import load_machine_config, load_policy, require_roots
from ..errors import HoudiniNotFoundError, ValidationError
from ..houdini import find_newest_houdini, format_version
from ..truth.filesystem import FilesystemSourceOfTruth


@dataclass
class CreationResult:
    """What was created, plus anything the caller should be told about it."""

    record: object
    warnings: list = field(default_factory=list)


def resolve_root_name(root_name, roots):
    """Picks the root to create in, or raises when the choice is ambiguous.

    Optional with exactly one declared root, because naming the only root that
    exists is ceremony and there is no ambiguity to protect against. Required
    from two roots up: a silent "first in the list" default is precisely the
    hidden assumption that a second root exists to expose.
    """
    if root_name is not None:
        return root_name

    if len(roots) == 1:
        return next(iter(roots))

    available = ", ".join(sorted(roots))
    raise ValidationError(
        f"{len(roots)} production roots are declared, so the target has to be "
        f"named explicitly. Declared roots: {available}."
    )


def detect_houdini_version(apps_dir=None):
    """Returns (version_string_or_none, warning_or_none).

    A missing Houdini is not fatal to project creation. Tying the creation of a
    project to an installed DCC would break headless automation, since a job
    scheduler can perfectly well create projects on a machine without Houdini.
    The field is written as null and the fallback to "newest installed" applies
    later, at the moment the project is actually opened.
    """
    try:
        version, _ = find_newest_houdini(apps_dir)
    except HoudiniNotFoundError as exc:
        return None, (
            f"No Houdini found, so this project has no pinned version: {exc}"
        )
    return format_version(version), None


def create_project(
    code,
    name,
    root_name=None,
    machine_config=None,
    policy=None,
    apps_dir=None,
    truth=None,
):
    """Validates, resolves and creates. Returns a CreationResult or raises.

    Every argument after the first three exists so that tests and other front
    ends can inject their own context. Left alone, the real policy, the real
    machine configuration and the real Houdini are used.
    """
    policy = load_policy() if policy is None else policy
    code = naming.validate_project_code(code, policy["project_code"])
    name = naming.validate_project_name(name)

    config = load_machine_config() if machine_config is None else machine_config
    roots = require_roots(config)
    root_name = resolve_root_name(root_name, roots)

    houdini_version, warning = detect_houdini_version(apps_dir)
    warnings = [warning] if warning else []

    truth = FilesystemSourceOfTruth(roots) if truth is None else truth
    record = truth.create_project(code, name, root_name, houdini_version)

    return CreationResult(record=record, warnings=warnings)


def list_projects(machine_config=None, truth=None):
    """Returns the ScanResult for every declared root.

    Reading side of the same layer. Tolerates a partial view on purpose, so it
    raises only when there is nowhere at all to look.
    """
    config = load_machine_config() if machine_config is None else machine_config
    roots = require_roots(config)
    truth = FilesystemSourceOfTruth(roots) if truth is None else truth
    return truth.list_projects()
