"""The shipped policy file parses and carries the sealed vocabulary.

This tests the data file itself, not the loader. A typo in pipeline.json breaks
every command at once, and it is the kind of typo that no other test would
attribute to the right cause.
"""

import json
import unittest
from pathlib import Path

import wpipeline

POLICY_PATH = Path(wpipeline.__file__).parent / "policy" / "pipeline.json"


class TestShippedPolicy(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_the_file_ships_inside_the_package(self):
        # Resolved relative to the package, never to the working directory:
        # the tool has to answer the same from any folder.
        self.assertTrue(POLICY_PATH.is_file())

    def test_schema_version_is_declared(self):
        self.assertEqual(self.policy["schema_version"], 1)

    def test_project_code_grammar(self):
        grammar = self.policy["project_code"]
        self.assertEqual(grammar["length"], 3)
        self.assertEqual(grammar["alphabet"], "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertIn("DEV", grammar["reserved"])

    def test_closed_vocabularies(self):
        # Sealed lists. Projects pick from them and never invent codes.
        self.assertEqual(self.policy["asset_types"], ["char", "prop", "env", "fx"])
        self.assertIn("fx", self.policy["departments"])
        self.assertIn("lgt", self.policy["departments"])

    def test_version_padding(self):
        self.assertEqual(self.policy["version_padding"], 3)


if __name__ == "__main__":
    unittest.main()
