"""Houdini version detection.

parse_version is tested against a synthetic list of folder names, the same way
stage 0 tested it: this machine has exactly one Houdini installed, so the
"pick the newest" branch is never exercised by reality and has to be exercised
by invention.
"""

import tempfile
import unittest
from pathlib import Path

from wpipeline import houdini
from wpipeline.errors import HoudiniNotFoundError


class TestParseVersion(unittest.TestCase):
    def test_a_real_version_name(self):
        self.assertEqual(houdini.parse_version("Houdini21.0.671"), (21, 0, 671))

    def test_names_that_are_not_versions(self):
        # Every one of these really sits in /Applications/Houdini.
        for name in ("Current", "Icon", "Houdini21.0", ".DS_Store", ""):
            with self.subTest(name=name):
                self.assertIsNone(houdini.parse_version(name))

    def test_the_pattern_is_anchored(self):
        # Without anchors, a name that merely contains a version would pass.
        for name in ("XHoudini21.0.671", "Houdini21.0.671X", "Houdini21.0.671.2"):
            with self.subTest(name=name):
                self.assertIsNone(houdini.parse_version(name))

    def test_ordering_is_numeric_and_not_lexicographic(self):
        # The classic silent bug: as text, '21.0.671' beats '21.0.1000'.
        older = houdini.parse_version("Houdini21.0.671")
        newer = houdini.parse_version("Houdini21.0.1000")
        self.assertLess(older, newer)
        self.assertLess("21.0.1000", "21.0.671")  # the wrong way, for contrast


class TestFormatVersion(unittest.TestCase):
    def test_tuple_becomes_the_string_written_to_disk(self):
        self.assertEqual(houdini.format_version((21, 0, 671)), "21.0.671")

    def test_round_trip(self):
        name = "Houdini20.5.332"
        version = houdini.parse_version(name)
        self.assertEqual(houdini.format_version(version), "20.5.332")


class TestFindNewestHoudini(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.apps = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _install(self, *names):
        for name in names:
            (self.apps / name).mkdir()

    def test_picks_the_newest_by_number(self):
        self._install(
            "Houdini20.5.332",
            "Houdini21.0.671",
            "Houdini21.0.1000",
            "Current",
            "Icon",
        )
        version, folder = houdini.find_newest_houdini(self.apps)
        self.assertEqual(version, (21, 0, 1000))
        self.assertEqual(folder.name, "Houdini21.0.1000")

    def test_ignores_everything_that_is_not_a_version(self):
        self._install("Houdini19.5.805", "Current", "Icon", "Houdini21.0")
        version, _ = houdini.find_newest_houdini(self.apps)
        self.assertEqual(version, (19, 5, 805))

    def test_raises_when_the_folder_is_missing(self):
        missing = self.apps / "nope"
        with self.assertRaises(HoudiniNotFoundError) as caught:
            houdini.find_newest_houdini(missing)
        self.assertIn(str(missing), str(caught.exception))

    def test_raises_when_no_version_is_recognizable(self):
        self._install("Current", "Icon")
        with self.assertRaises(HoudiniNotFoundError):
            houdini.find_newest_houdini(self.apps)

    def test_it_raises_instead_of_exiting(self):
        # The contract that lets this run inside Houdini: a SystemExit here
        # would take the artist's session with it.
        with self.assertRaises(HoudiniNotFoundError):
            houdini.find_newest_houdini(self.apps / "nope")


if __name__ == "__main__":
    unittest.main()
