"""ProjectRecord: the six sealed fields, and the two that must never be saved.

The load-bearing test here is that serialization writes exactly six keys. It is
the only thing standing between a derived value and an immutable file on disk.
"""

import unittest
from pathlib import Path

from wpipeline.errors import CorruptProjectFileError
from wpipeline.truth.record import FILE_FIELDS, ProjectRecord, ScanResult

VALID = {
    "schema_version": 1,
    "code": "DEM",
    "name": "Demo Project",
    "root": "main",
    "houdini_version": "21.0.671",
    "created": "2026-08-07T12:00:00+00:00",
}


class TestSerialization(unittest.TestCase):
    def record(self, **overrides):
        data = dict(VALID)
        data.update(overrides)
        return ProjectRecord(
            found_in_root="main", path=Path("/tmp/main/DEM"), **data
        )

    def test_writes_exactly_the_six_sealed_fields(self):
        written = self.record().to_file_data()
        self.assertEqual(sorted(written), sorted(FILE_FIELDS))
        self.assertEqual(len(written), 6)

    def test_derived_values_never_reach_disk(self):
        # path is computed from configuration; found_in_root is where the scan
        # read the file. Neither may be persisted, or an immutable file would
        # go stale the day the volume is renamed.
        written = self.record().to_file_data()
        self.assertNotIn("path", written)
        self.assertNotIn("found_in_root", written)
        self.assertNotIn("/tmp/main", str(written))

    def test_round_trip(self):
        record = self.record()
        again = ProjectRecord.from_file_data(
            record.to_file_data(),
            found_in_root="main",
            path=Path("/tmp/main/DEM"),
            source_path=Path("/tmp/main/DEM/project.json"),
        )
        self.assertEqual(again, record)

    def test_a_null_houdini_version_survives(self):
        written = self.record(houdini_version=None).to_file_data()
        self.assertIsNone(written["houdini_version"])


class TestFromFileData(unittest.TestCase):
    def build(self, data):
        return ProjectRecord.from_file_data(
            data,
            found_in_root="main",
            path=Path("/tmp/main/DEM"),
            source_path=Path("/tmp/main/DEM/project.json"),
        )

    def test_accepts_a_complete_file(self):
        record = self.build(dict(VALID))
        self.assertEqual(record.code, "DEM")
        self.assertEqual(record.found_in_root, "main")

    def test_every_missing_field_is_reported(self):
        for field in FILE_FIELDS:
            with self.subTest(field=field):
                data = dict(VALID)
                del data[field]
                with self.assertRaises(CorruptProjectFileError) as caught:
                    self.build(data)
                self.assertIn(field, str(caught.exception))

    def test_the_message_carries_the_exact_path(self):
        data = dict(VALID)
        del data["created"]
        with self.assertRaises(CorruptProjectFileError) as caught:
            self.build(data)
        self.assertIn("project.json", str(caught.exception))

    def test_rejects_non_objects(self):
        for data in ([], "text", 5):
            with self.subTest(data=data):
                with self.assertRaises(CorruptProjectFileError):
                    self.build(data)


class TestRootAgreement(unittest.TestCase):
    def test_agrees_when_the_field_matches_the_location(self):
        record = ProjectRecord(found_in_root="main", path=None, **VALID)
        self.assertTrue(record.root_matches_location)

    def test_disagrees_when_the_project_was_moved_by_hand(self):
        record = ProjectRecord(found_in_root="internal", path=None, **VALID)
        self.assertFalse(record.root_matches_location)


class TestScanResult(unittest.TestCase):
    def build(self, **overrides):
        data = {
            "projects": [],
            "warnings": [],
            "unreadable_roots": [],
            "damaged_files": [],
        }
        data.update(overrides)
        return ScanResult(**data)

    def test_a_clean_scan_is_neither_partial_nor_damaged(self):
        result = self.build()
        self.assertFalse(result.partial)
        self.assertFalse(result.has_damage)

    def test_an_unreadable_root_makes_it_partial(self):
        result = self.build(warnings=["gone"], unreadable_roots=["main"])
        self.assertTrue(result.partial)
        self.assertTrue(result.has_damage)

    def test_a_damaged_file_is_damage_without_being_partial(self):
        # Every root was read, but something in one of them cannot be trusted.
        result = self.build(warnings=["broken"], damaged_files=["/tmp/p.json"])
        self.assertFalse(result.partial)
        self.assertTrue(result.has_damage)

    def test_a_disagreement_warns_without_blocking_writes(self):
        # A project whose root field does not match where it was found reads
        # fine, so its code is known and uniqueness still holds. It warns, but
        # it must not stop create-project.
        result = self.build(warnings=["declares root 'main', found in 'internal'"])
        self.assertFalse(result.has_damage)
        self.assertTrue(result.warnings)


if __name__ == "__main__":
    unittest.main()
