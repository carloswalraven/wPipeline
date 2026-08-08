"""The create-project orchestration, with no terminal in sight.

Houdini detection is pointed at temporary folders, so these tests say the same
thing on a machine with Houdini and on one without.
"""

import json
import tempfile
import unittest
from pathlib import Path

from wpipeline.commands import create_project as command
from wpipeline.config import MachineConfig, SOURCE_USER_FILE, load_policy
from wpipeline.errors import ConfigError, SourceOfTruthError, ValidationError
from wpipeline.truth.filesystem import PROJECT_FILE

POLICY = load_policy()


class CommandTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        self.main = self.base / "main"
        self.internal = self.base / "internal"
        self.main.mkdir()
        self.internal.mkdir()

        self.no_houdini = self.base / "no_houdini"
        self.houdini = self.base / "houdini"
        self.houdini.mkdir()
        (self.houdini / "Houdini21.0.671").mkdir()

    def config(self, **roots):
        return MachineConfig(roots=roots or {"main": self.main}, source=SOURCE_USER_FILE)

    def create(self, code="DEM", name="Demo", root_name=None, config=None, apps=None):
        return command.create_project(
            code,
            name,
            root_name=root_name,
            machine_config=self.config() if config is None else config,
            policy=POLICY,
            apps_dir=self.no_houdini if apps is None else apps,
        )


class TestHappyPath(CommandTestCase):
    def test_creates_and_returns_the_record(self):
        result = self.create()
        self.assertEqual(result.record.code, "DEM")
        self.assertEqual(result.record.root, "main")
        self.assertTrue((self.main / "DEM" / PROJECT_FILE).is_file())

    def test_pins_the_detected_houdini_version(self):
        result = self.create(apps=self.houdini)
        self.assertEqual(result.record.houdini_version, "21.0.671")
        self.assertEqual(result.warnings, [])

    def test_without_houdini_it_writes_null_and_warns(self):
        # Tying creation to an installed DCC would break headless automation.
        result = self.create(apps=self.no_houdini)
        self.assertIsNone(result.record.houdini_version)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("no pinned version", result.warnings[0])

        written = json.loads((self.main / "DEM" / PROJECT_FILE).read_text())
        self.assertIsNone(written["houdini_version"])

    def test_the_name_is_trimmed_but_kept_as_typed(self):
        result = self.create(name="  Proyecto Demo  ")
        self.assertEqual(result.record.name, "Proyecto Demo")


class TestValidationHappensFirst(CommandTestCase):
    def test_a_bad_code_never_reaches_disk(self):
        for code in ("dem", "DEMO", "D1M", "DEV"):
            with self.subTest(code=code):
                with self.assertRaises(ValidationError):
                    self.create(code=code)
        self.assertEqual(list(self.main.iterdir()), [])

    def test_an_empty_name_never_reaches_disk(self):
        with self.assertRaises(ValidationError):
            self.create(name="   ")
        self.assertEqual(list(self.main.iterdir()), [])

    def test_zero_roots_is_an_instructive_error(self):
        empty = MachineConfig(roots={}, source=SOURCE_USER_FILE)
        with self.assertRaises(ConfigError) as caught:
            self.create(config=empty)
        self.assertIn("roots", str(caught.exception))


class TestRootResolution(CommandTestCase):
    def test_one_root_needs_no_flag(self):
        result = self.create(config=self.config(main=self.main))
        self.assertEqual(result.record.root, "main")

    def test_two_roots_without_a_choice_is_refused(self):
        two = self.config(main=self.main, internal=self.internal)
        with self.assertRaises(ValidationError) as caught:
            self.create(config=two)

        message = str(caught.exception)
        self.assertIn("main", message)
        self.assertIn("internal", message)
        # Refused, not silently defaulted to the first one.
        self.assertEqual(list(self.main.iterdir()), [])
        self.assertEqual(list(self.internal.iterdir()), [])

    def test_two_roots_with_a_choice_works(self):
        two = self.config(main=self.main, internal=self.internal)
        result = self.create(root_name="internal", config=two)
        self.assertEqual(result.record.root, "internal")
        self.assertTrue((self.internal / "DEM").is_dir())
        self.assertFalse((self.main / "DEM").exists())

    def test_resolve_root_name_directly(self):
        self.assertEqual(command.resolve_root_name(None, {"only": Path("/tmp")}), "only")
        self.assertEqual(
            command.resolve_root_name("b", {"a": Path("/tmp"), "b": Path("/tmp")}), "b"
        )
        with self.assertRaises(ValidationError):
            command.resolve_root_name(None, {"a": Path("/tmp"), "b": Path("/tmp")})


class TestListProjects(CommandTestCase):
    def test_lists_what_was_created(self):
        two = self.config(main=self.main, internal=self.internal)
        self.create(code="DEM", root_name="main", config=two)
        self.create(code="TST", root_name="internal", config=two)

        result = command.list_projects(machine_config=two)
        self.assertEqual(sorted(p.code for p in result.projects), ["DEM", "TST"])
        self.assertFalse(result.has_damage)

    def test_listing_survives_a_missing_root(self):
        # Create while the view is complete, then break it. The other order
        # cannot work, and that is the sealed rule rather than an accident:
        # writing demands certainty, reading does not.
        self.create(code="DEM", root_name="main", config=self.config(main=self.main))

        broken = self.config(main=self.main, gone=self.base / "absent")
        result = command.list_projects(machine_config=broken)

        self.assertEqual([p.code for p in result.projects], ["DEM"])
        self.assertTrue(result.partial)
        self.assertEqual(result.unreadable_roots, ["gone"])

    def test_creating_is_refused_while_a_root_is_missing(self):
        # The consequence stated up front: with the external volume out of
        # sight, nothing can be created, not even in a root that is available.
        broken = self.config(main=self.main, gone=self.base / "absent")
        with self.assertRaises(SourceOfTruthError):
            self.create(code="DEM", root_name="main", config=broken)
        self.assertEqual(list(self.main.iterdir()), [])

    def test_zero_roots_refuses_to_list(self):
        empty = MachineConfig(roots={}, source=SOURCE_USER_FILE)
        with self.assertRaises(ConfigError):
            command.list_projects(machine_config=empty)


class TestDetectHoudiniVersion(CommandTestCase):
    def test_found(self):
        version, warning = command.detect_houdini_version(self.houdini)
        self.assertEqual(version, "21.0.671")
        self.assertIsNone(warning)

    def test_not_found(self):
        version, warning = command.detect_houdini_version(self.no_houdini)
        self.assertIsNone(version)
        self.assertIn("No Houdini found", warning)


if __name__ == "__main__":
    unittest.main()
