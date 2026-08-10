"""The command line, exercised the way it is really invoked.

These run `python3 -m wpipeline` in a subprocess rather than calling main()
directly, because the things being checked here are exit codes, stream
separation and the shape of stdout, and none of those are real until a process
actually exits.

WPIPELINE_CONFIG points every run at a temporary configuration, so the real
machine configuration is never read and no real root is ever written to.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from wpipeline.truth.record import FILE_FIELDS

REPO_ROOT = Path(__file__).resolve().parent.parent


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        self.main = self.base / "main"
        self.internal = self.base / "internal"
        self.main.mkdir()
        self.internal.mkdir()

        self.config_path = self.write_config({"main": str(self.main)})

    def write_config(self, roots, name="machine.json"):
        path = self.base / name
        path.write_text(
            json.dumps({"schema_version": 1, "roots": roots}), encoding="utf-8"
        )
        return path

    def run_cli(self, *args, config=None):
        env = dict(os.environ)
        env["WPIPELINE_CONFIG"] = str(self.config_path if config is None else config)
        env["PYTHONPATH"] = str(REPO_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "wpipeline", *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(self.base),  # never the repo, to prove PYTHONPATH is enough
        )


class TestCreateProject(CliTestCase):
    def test_creates_and_exits_zero(self):
        done = self.run_cli("create-project", "DEM", "--name", "Demo Project")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("Created project DEM", done.stdout)
        self.assertTrue((self.main / "DEM" / "project.json").is_file())

    def test_json_output_is_one_parseable_object(self):
        done = self.run_cli("create-project", "DEM", "--name", "Demo", "--json")
        self.assertEqual(done.returncode, 0, done.stderr)

        payload = json.loads(done.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["project"]["code"], "DEM")
        self.assertEqual(payload["project"]["root"], "main")
        # Six sealed fields in the project object; path travels beside it.
        self.assertEqual(len(payload["project"]), 6)
        self.assertIn("path", payload)

    def test_a_bad_code_exits_one_with_a_readable_error(self):
        done = self.run_cli("create-project", "dem", "--name", "Demo")
        self.assertEqual(done.returncode, 1)
        self.assertIn("ERROR", done.stderr)
        self.assertEqual(done.stdout, "")
        self.assertEqual(list(self.main.iterdir()), [])

    def test_errors_are_json_too_when_json_is_asked_for(self):
        # A caller parsing stdout has to get the whole story from one stream,
        # or headless automation is back to parsing prose.
        done = self.run_cli("create-project", "DEV", "--name", "Demo", "--json")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(done.stderr, "")

        payload = json.loads(done.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "ValidationError")
        self.assertIn("reserved", payload["message"].lower())

    def test_a_duplicate_code_is_refused(self):
        self.run_cli("create-project", "DEM", "--name", "Demo")
        done = self.run_cli("create-project", "DEM", "--name", "Again", "--json")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(json.loads(done.stdout)["error"], "ProjectExistsError")

    def test_name_is_required(self):
        done = self.run_cli("create-project", "DEM")
        self.assertEqual(done.returncode, 2)  # argparse usage error


class TestRootFlag(CliTestCase):
    def setUp(self):
        super().setUp()
        self.two_roots = self.write_config(
            {"main": str(self.main), "internal": str(self.internal)}, name="two.json"
        )

    def test_one_root_needs_no_flag(self):
        done = self.run_cli("create-project", "DEM", "--name", "Demo")
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_two_roots_without_the_flag_is_refused(self):
        done = self.run_cli(
            "create-project", "DEM", "--name", "Demo", "--json", config=self.two_roots
        )
        self.assertEqual(done.returncode, 1)
        message = json.loads(done.stdout)["message"]
        self.assertIn("main", message)
        self.assertIn("internal", message)

    def test_two_roots_with_the_flag_works(self):
        done = self.run_cli(
            "create-project",
            "TST",
            "--name",
            "Test",
            "--root",
            "internal",
            "--json",
            config=self.two_roots,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["project"]["root"], "internal")
        self.assertTrue((self.internal / "TST").is_dir())

    def test_an_unknown_root_is_refused(self):
        done = self.run_cli(
            "create-project",
            "TST",
            "--name",
            "Test",
            "--root",
            "nowhere",
            "--json",
            config=self.two_roots,
        )
        self.assertEqual(done.returncode, 1)
        self.assertEqual(json.loads(done.stdout)["error"], "RootError")


class TestListProjects(CliTestCase):
    def test_empty_is_not_an_error(self):
        done = self.run_cli("list-projects")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("No projects found", done.stdout)

    def test_lists_what_exists(self):
        self.run_cli("create-project", "DEM", "--name", "Demo Project")
        done = self.run_cli("list-projects")
        self.assertEqual(done.returncode, 0)
        self.assertIn("DEM", done.stdout)
        self.assertIn("Demo Project", done.stdout)

    def test_json_listing(self):
        self.run_cli("create-project", "DEM", "--name", "Demo")
        done = self.run_cli("list-projects", "--json")
        payload = json.loads(done.stdout)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["partial"])
        self.assertEqual(payload["projects"][0]["project"]["code"], "DEM")

    def test_json_project_object_has_exactly_the_six_sealed_fields(self):
        # Same shape as create-project --json: project and path sit side by
        # side, so the project object is identical to what is on disk.
        self.run_cli("create-project", "DEM", "--name", "Demo")
        done = self.run_cli("list-projects", "--json")
        payload = json.loads(done.stdout)
        entry = payload["projects"][0]
        self.assertEqual(sorted(entry["project"]), sorted(FILE_FIELDS))
        self.assertIn("path", entry)

    def test_a_missing_root_is_reported_and_still_exits_zero(self):
        self.run_cli("create-project", "DEM", "--name", "Demo")
        broken = self.write_config(
            {"main": str(self.main), "gone": str(self.base / "absent")}, name="bad.json"
        )
        done = self.run_cli("list-projects", config=broken)

        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("DEM", done.stdout)
        self.assertIn("PARTIAL", done.stdout)
        self.assertIn("gone", done.stdout)

    def test_creating_while_a_root_is_missing_exits_one(self):
        broken = self.write_config(
            {"main": str(self.main), "gone": str(self.base / "absent")}, name="bad.json"
        )
        # --root is given, so the ambiguity check passes and the scan is what
        # refuses: writing needs every root in view, even the one not targeted.
        done = self.run_cli(
            "create-project",
            "DEM",
            "--name",
            "Demo",
            "--root",
            "main",
            "--json",
            config=broken,
        )
        self.assertEqual(done.returncode, 1)
        self.assertEqual(json.loads(done.stdout)["error"], "SourceOfTruthError")
        self.assertFalse((self.main / "DEM").exists())


class TestConfigurationErrors(CliTestCase):
    def test_a_missing_config_file_named_by_the_variable_is_an_error(self):
        done = self.run_cli(
            "list-projects", "--json", config=self.base / "does_not_exist.json"
        )
        self.assertEqual(done.returncode, 1)
        payload = json.loads(done.stdout)
        self.assertEqual(payload["error"], "ConfigError")
        self.assertIn("WPIPELINE_CONFIG", payload["message"])

    def test_zero_roots_prints_the_instructions(self):
        empty = self.write_config({}, name="empty.json")
        done = self.run_cli("list-projects", config=empty)
        self.assertEqual(done.returncode, 1)
        self.assertIn("machine.json", done.stderr)
        self.assertIn('"roots"', done.stderr)


class TestInvocation(unittest.TestCase):
    def test_help_works_without_any_configuration(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT)
        env.pop("WPIPELINE_CONFIG", None)
        done = subprocess.run(
            [sys.executable, "-m", "wpipeline", "--help"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(done.returncode, 0)
        self.assertIn("create-project", done.stdout)
        self.assertIn("list-projects", done.stdout)

    def test_importing_the_package_runs_nothing(self):
        # The whole reason this is a package: importing it must be inert, so a
        # Houdini session can import it without anything happening.
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT)
        done = subprocess.run(
            [sys.executable, "-c", "import wpipeline; print('inert')"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(done.stdout.strip(), "inert")


if __name__ == "__main__":
    unittest.main()
