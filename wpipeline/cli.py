"""The command line surface: one command with subcommands.

This is the only layer that prints and the only one that decides an exit code.
Everything below raises. That split is what lets the same validation answer a
terminal today and a Houdini panel later, without the rules being copied into
UI callbacks.

Two output modes, and the difference matters more than it looks. Plain text is
for a human reading a terminal. With --json, everything goes to stdout as one
JSON object, errors included, because headless automation demands that a caller
never has to parse prose to find out what happened.
"""

import argparse
import json
import sys

from .commands import create_project as command
from .errors import WPipelineError


def build_parser():
    """Builds the argument parser for the whole tool."""
    parser = argparse.ArgumentParser(
        prog="wpipeline",
        description="wPipeline - project gatekeeper for Houdini.",
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--json",
        action="store_true",
        help="print one JSON object on stdout, errors included",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser(
        "create-project",
        parents=[common],
        help="create a project folder, its project file and assets/ and seq/",
    )
    create.add_argument("code", help="project code: exactly 3 letters, A-Z")
    create.add_argument(
        "--name", required=True, help="readable project name, any language"
    )
    create.add_argument(
        "--root",
        default=None,
        help=(
            "logical name of the production root to create in. Optional when "
            "a single root is declared, required when there are more"
        ),
    )

    subparsers.add_parser(
        "list-projects",
        parents=[common],
        help="list every project found by scanning the declared roots",
    )

    return parser


def main(argv=None):
    """Runs the tool and returns the exit code. Never raises WPipelineError."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create-project":
            return _run_create(args)
        return _run_list(args)
    except WPipelineError as exc:
        return _report_error(exc, args.command, args.json)


def _run_create(args):
    result = command.create_project(args.code, args.name, root_name=args.root)
    record = result.record

    if args.json:
        _print_json(
            {
                "ok": True,
                "command": "create-project",
                "project": record.to_file_data(),
                "path": str(record.path),
                "warnings": result.warnings,
            }
        )
        return 0

    print(f"Created project {record.code} in root '{record.root}'")
    print(f"  Path            : {record.path}")
    print(f"  Name            : {record.name}")
    print(f"  Houdini version : {record.houdini_version or 'not pinned'}")
    print(f"  Created         : {record.created}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    return 0


def _run_list(args):
    result = command.list_projects()

    if args.json:
        _print_json(
            {
                "ok": True,
                "command": "list-projects",
                "partial": result.partial,
                "projects": [
                    {"project": record.to_file_data(), "path": str(record.path)}
                    for record in result.projects
                ],
                "unreadable_roots": result.unreadable_roots,
                "warnings": result.warnings,
            }
        )
        return 0

    if result.projects:
        for record in result.projects:
            version = record.houdini_version or "not pinned"
            print(f"{record.code}  {record.found_in_root:<10} {version:<10} {record.name}")
            print(f"      {record.path}")
    else:
        print("No projects found.")

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    if result.partial:
        # Said out loud rather than implied by a shorter list: an incomplete
        # answer is only useful when it is labelled as incomplete.
        print(
            "This list is PARTIAL: "
            f"{', '.join(result.unreadable_roots)} could not be read."
        )
    return 0


def _report_error(exc, command_name, as_json):
    """Prints a failure the way the chosen output mode requires."""
    if as_json:
        # Errors go to stdout too, so a caller parsing stdout gets the whole
        # story from one stream.
        _print_json(
            {
                "ok": False,
                "command": command_name,
                "error": type(exc).__name__,
                "message": str(exc),
            }
        )
    else:
        print(f"\nERROR: {exc}\n", file=sys.stderr)
    return 1


def _print_json(payload):
    print(json.dumps(payload, indent=2))
