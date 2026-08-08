"""The filesystem source of truth: one case per sealed decision.

Everything runs against temporary roots. Nothing here reads the real machine
configuration or the real production volume.
"""

import json
import tempfile
import unittest
from pathlib import Path

from wpipeline.errors import (
    PathConflictError,
    ProjectExistsError,
    RootError,
    SourceOfTruthError,
)
from wpipeline.truth.filesystem import (
    PROJECT_FILE,
    FilesystemSourceOfTruth,
    describe_root_problem,
    utc_timestamp,
    volume_root,
)


def project_data(code, root="main", **overrides):
    data = {
        "schema_version": 1,
        "code": code,
        "name": f"Project {code}",
        "root": root,
        "houdini_version": "21.0.671",
        "created": "2026-08-07T12:00:00+00:00",
    }
    data.update(overrides)
    return data


class TruthTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

        self.main = self.base / "main"
        self.internal = self.base / "internal"
        self.main.mkdir()
        self.internal.mkdir()
        self.roots = {"main": self.main, "internal": self.internal}

    def truth(self, roots=None):
        return FilesystemSourceOfTruth(self.roots if roots is None else roots)

    def make_project(self, root, code, data=None, root_name="main"):
        folder = root / code
        folder.mkdir()
        (folder / "assets").mkdir()
        (folder / "seq").mkdir()
        payload = project_data(code, root=root_name) if data is None else data
        if isinstance(payload, str):
            (folder / PROJECT_FILE).write_text(payload, encoding="utf-8")
        else:
            (folder / PROJECT_FILE).write_text(json.dumps(payload), encoding="utf-8")
        return folder


class TestVolumeRoot(unittest.TestCase):
    def test_a_path_on_a_volume(self):
        self.assertEqual(
            volume_root(Path("/Volumes/W_AirProjects/Dropbox/x")),
            Path("/Volumes/W_AirProjects"),
        )

    def test_a_path_that_is_not_on_a_volume(self):
        # The internal root lives on the boot disk, so this is the normal case
        # for it and must not be mistaken for an unmounted volume.
        self.assertIsNone(volume_root(Path("/Users/someone/projects")))


class TestRootProblems(TruthTestCase):
    def test_a_healthy_root_has_no_problem(self):
        self.assertIsNone(describe_root_problem(self.main))

    def test_a_missing_folder_is_reported_as_missing(self):
        problem = describe_root_problem(self.base / "absent")
        self.assertIn("does not exist", problem)

    def test_a_file_where_a_folder_belongs(self):
        impostor = self.base / "afile"
        impostor.write_text("x", encoding="utf-8")
        self.assertIn("not a folder", describe_root_problem(impostor))

    def test_an_unmounted_volume_says_so(self):
        # Told apart from "the folder does not exist" because the fixes differ:
        # one is a cable, the other is a mistake in configuration.
        problem = describe_root_problem(Path("/Volumes/NotMountedXYZ/projects"))
        self.assertIn("not mounted", problem)


class TestScanning(TruthTestCase):
    def test_an_empty_root_is_not_an_error(self):
        result = self.truth().list_projects()
        self.assertEqual(result.projects, [])
        self.assertFalse(result.has_damage)
        self.assertEqual(result.warnings, [])

    def test_finds_a_valid_project(self):
        self.make_project(self.main, "DEM")
        result = self.truth().list_projects()
        self.assertEqual([p.code for p in result.projects], ["DEM"])
        record = result.projects[0]
        self.assertEqual(record.found_in_root, "main")
        self.assertEqual(record.path, self.main / "DEM")

    def test_finds_projects_across_every_root(self):
        self.make_project(self.main, "DEM")
        self.make_project(self.internal, "TST", root_name="internal")
        result = self.truth().list_projects()
        self.assertEqual(sorted(p.code for p in result.projects), ["DEM", "TST"])

    def test_a_folder_without_a_project_file_is_ignored_without_noise(self):
        # This is the real _etapa0_test case: it lives in the production root
        # and is not a project.
        (self.main / "_etapa0_test").mkdir()
        (self.main / "_etapa0_test" / "publish").mkdir()
        result = self.truth().list_projects()
        self.assertEqual(result.projects, [])
        self.assertEqual(result.warnings, [])
        self.assertFalse(result.has_damage)

    def test_loose_files_in_a_root_are_ignored(self):
        (self.main / ".DS_Store").write_text("junk", encoding="utf-8")
        self.assertEqual(self.truth().list_projects().projects, [])

    def test_the_scan_is_one_level_deep(self):
        # A project file buried deeper must not be found: recursive sweeps in
        # Dropbox are slow and can pull down online-only files.
        buried = self.main / "outer" / "inner"
        buried.mkdir(parents=True)
        (buried / PROJECT_FILE).write_text(
            json.dumps(project_data("DEP")), encoding="utf-8"
        )
        self.assertEqual(self.truth().list_projects().projects, [])

    def test_invalid_json_warns_and_the_scan_continues(self):
        self.make_project(self.main, "DEM")
        self.make_project(self.main, "BAD", data="{ not json")
        result = self.truth().list_projects()

        self.assertEqual([p.code for p in result.projects], ["DEM"])
        self.assertTrue(result.has_damage)
        self.assertEqual(len(result.damaged_files), 1)
        self.assertIn("BAD", result.warnings[0])

    def test_a_missing_field_warns_with_the_exact_path(self):
        data = project_data("BAD")
        del data["created"]
        self.make_project(self.main, "BAD", data=data)
        result = self.truth().list_projects()

        self.assertEqual(result.projects, [])
        self.assertTrue(result.has_damage)
        self.assertIn("created", result.warnings[0])
        self.assertIn(str(self.main / "BAD" / PROJECT_FILE), result.warnings[0])

    def test_an_unreadable_root_makes_the_answer_partial(self):
        # Listing still works: an incomplete answer labelled as incomplete is
        # more useful than a refusal.
        self.make_project(self.main, "DEM")
        truth = self.truth({"main": self.main, "gone": self.base / "absent"})
        result = truth.list_projects()

        self.assertEqual([p.code for p in result.projects], ["DEM"])
        self.assertTrue(result.partial)
        self.assertEqual(result.unreadable_roots, ["gone"])
        self.assertIn("gone", result.warnings[0])

    def test_a_root_field_that_disagrees_warns_without_being_damage(self):
        # Moved by hand: the file reads fine and its code is known, so
        # uniqueness still holds.
        self.make_project(self.internal, "DEM", root_name="main")
        result = self.truth().list_projects()

        self.assertEqual([p.code for p in result.projects], ["DEM"])
        self.assertFalse(result.has_damage)
        self.assertEqual(len(result.warnings), 1)
        self.assertIn("declares root 'main'", result.warnings[0])


class TestGetProject(TruthTestCase):
    def test_finds_by_code(self):
        self.make_project(self.main, "DEM")
        record = self.truth().get_project("DEM")
        self.assertEqual(record.name, "Project DEM")

    def test_returns_none_when_absent(self):
        self.assertIsNone(self.truth().get_project("DEM"))


class TestCreateProject(TruthTestCase):
    def test_creates_the_folder_the_file_and_the_two_children(self):
        record = self.truth().create_project("DEM", "Demo", "main", "21.0.671")
        folder = self.main / "DEM"

        self.assertTrue(folder.is_dir())
        self.assertTrue((folder / "assets").is_dir())
        self.assertTrue((folder / "seq").is_dir())
        self.assertTrue((folder / PROJECT_FILE).is_file())
        self.assertEqual(record.path, folder)

    def test_writes_nothing_beyond_the_sealed_shape(self):
        # No asset types, no dev sequence: stage 1b creates those on the fly.
        self.truth().create_project("DEM", "Demo", "main", "21.0.671")
        children = sorted(p.name for p in (self.main / "DEM").iterdir())
        self.assertEqual(children, ["assets", PROJECT_FILE, "seq"])

    def test_the_project_file_carries_exactly_six_fields(self):
        self.truth().create_project("DEM", "Demo", "main", "21.0.671")
        written = json.loads((self.main / "DEM" / PROJECT_FILE).read_text())
        self.assertEqual(
            sorted(written),
            ["code", "created", "houdini_version", "name", "root", "schema_version"],
        )
        self.assertEqual(written["root"], "main")
        self.assertNotIn(str(self.main), json.dumps(written))

    def test_a_null_houdini_version_is_written_as_null(self):
        self.truth().create_project("DEM", "Demo", "main", None)
        written = json.loads((self.main / "DEM" / PROJECT_FILE).read_text())
        self.assertIsNone(written["houdini_version"])

    def test_creating_in_the_second_root(self):
        record = self.truth().create_project("TST", "Test", "internal", None)
        self.assertTrue((self.internal / "TST" / PROJECT_FILE).is_file())
        self.assertEqual(record.root, "internal")
        self.assertFalse((self.main / "TST").exists())

    def test_the_new_project_is_immediately_visible(self):
        self.truth().create_project("DEM", "Demo", "main", None)
        self.assertIsNotNone(self.truth().get_project("DEM"))

    def test_an_unknown_root_is_refused(self):
        with self.assertRaises(RootError) as caught:
            self.truth().create_project("DEM", "Demo", "nowhere", None)
        self.assertIn("internal", str(caught.exception))
        self.assertIn("main", str(caught.exception))

    def test_a_taken_code_is_refused_and_says_where(self):
        self.make_project(self.main, "DEM")
        with self.assertRaises(ProjectExistsError) as caught:
            self.truth().create_project("DEM", "Demo", "internal", None)
        self.assertIn("main", str(caught.exception))
        # Uniqueness is global: the clash is in another root than the target.
        self.assertFalse((self.internal / "DEM").exists())

    def test_an_existing_folder_without_a_project_file_is_refused(self):
        (self.main / "DEM").mkdir()
        with self.assertRaises(PathConflictError):
            self.truth().create_project("DEM", "Demo", "main", None)
        # Not repaired: no project file was written into it.
        self.assertFalse((self.main / "DEM" / PROJECT_FILE).exists())

    def test_an_unreadable_root_blocks_creation_everywhere(self):
        # The sealed consequence: with a declared root out of sight, nothing
        # can be created, not even in a root that is perfectly available.
        truth = self.truth({"main": self.main, "gone": self.base / "absent"})
        with self.assertRaises(SourceOfTruthError) as caught:
            truth.create_project("DEM", "Demo", "main", None)
        self.assertIn("gone", str(caught.exception))
        self.assertFalse((self.main / "DEM").exists())

    def test_a_damaged_project_file_blocks_creation(self):
        # That file could be the very one declaring the code being requested.
        self.make_project(self.internal, "BAD", data="{ not json")
        with self.assertRaises(SourceOfTruthError):
            self.truth().create_project("DEM", "Demo", "main", None)
        self.assertFalse((self.main / "DEM").exists())

    def test_a_disagreeing_root_field_does_not_block_creation(self):
        self.make_project(self.internal, "OLD", root_name="main")
        record = self.truth().create_project("DEM", "Demo", "main", None)
        self.assertEqual(record.code, "DEM")

    def test_every_refusal_leaves_the_disk_untouched(self):
        # Checked by listing the root afterwards, not by trusting the message.
        before = sorted(p.name for p in self.main.iterdir())
        for root_name in ("nowhere",):
            with self.assertRaises(RootError):
                self.truth().create_project("DEM", "Demo", root_name, None)
        self.assertEqual(sorted(p.name for p in self.main.iterdir()), before)


class TestTimestamp(unittest.TestCase):
    def test_is_iso_utc_to_the_second(self):
        stamp = utc_timestamp()
        self.assertTrue(stamp.endswith("+00:00"))
        self.assertNotIn(".", stamp)  # no microseconds
        self.assertEqual(len(stamp), len("2026-08-07T12:00:00+00:00"))


if __name__ == "__main__":
    unittest.main()
