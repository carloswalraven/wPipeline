"""Project code and project name grammar.

The grammar is passed in, not imported, so these tests state the rules with a
literal grammar. If the shipped policy ever drifts from the sealed rules,
test_policy_file.py is what catches it.
"""

import unittest

from wpipeline import naming
from wpipeline.errors import ValidationError

GRAMMAR = {
    "length": 3,
    "alphabet": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "reserved": ["DEV"],
}


class TestProjectCode(unittest.TestCase):
    def test_accepts_three_uppercase_letters(self):
        for code in ("DEM", "ABC", "XYZ", "AAA"):
            with self.subTest(code=code):
                self.assertEqual(naming.validate_project_code(code, GRAMMAR), code)

    def test_rejects_wrong_length(self):
        for code in ("DE", "DEMO", "", "D"):
            with self.subTest(code=code):
                with self.assertRaises(ValidationError):
                    naming.validate_project_code(code, GRAMMAR)

    def test_rejects_lowercase_without_correcting_it(self):
        # 'dem' must not quietly become 'DEM': the prefix ends up welded to
        # every published file, so guessing is expensive and silent.
        with self.assertRaises(ValidationError):
            naming.validate_project_code("dem", GRAMMAR)
        with self.assertRaises(ValidationError):
            naming.validate_project_code("DEm", GRAMMAR)

    def test_rejects_digits(self):
        # Digits would allow 'S01', which reads as a sequence.
        for code in ("S01", "D3M", "123"):
            with self.subTest(code=code):
                with self.assertRaises(ValidationError):
                    naming.validate_project_code(code, GRAMMAR)

    def test_rejects_accents_and_symbols(self):
        # Non-ASCII input is written as escapes so that the source file itself
        # stays pure ASCII, which is the repo rule for code.
        for code in ("D\u00c9M", "D-M", "D M", "D_M"):
            with self.subTest(code=code):
                with self.assertRaises(ValidationError):
                    naming.validate_project_code(code, GRAMMAR)

    def test_rejects_the_reserved_code(self):
        with self.assertRaises(ValidationError) as caught:
            naming.validate_project_code("DEV", GRAMMAR)
        self.assertIn("reserved", str(caught.exception).lower())

    def test_rejects_non_text(self):
        for value in (None, 123, ["D", "E", "M"]):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    naming.validate_project_code(value, GRAMMAR)

    def test_the_message_names_the_offending_character(self):
        with self.assertRaises(ValidationError) as caught:
            naming.validate_project_code("D1M", GRAMMAR)
        self.assertIn("1", str(caught.exception))

    def test_the_grammar_comes_from_configuration(self):
        # Another studio's flavor: four letters, its own reserved word. Nothing
        # in naming.py should stand in the way.
        other = {
            "length": 4,
            "alphabet": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "reserved": ["TEST"],
        }
        self.assertEqual(naming.validate_project_code("SHOW", other), "SHOW")
        with self.assertRaises(ValidationError):
            naming.validate_project_code("DEM", other)
        with self.assertRaises(ValidationError):
            naming.validate_project_code("TEST", other)


class TestProjectName(unittest.TestCase):
    def test_accepts_free_text(self):
        self.assertEqual(naming.validate_project_name("Demo Project"), "Demo Project")

    def test_accepts_any_language_and_accents(self):
        # The name never touches disk: the folder is called after the code.
        for name in ("Proyecto Demo", "\u00c9l Drag\u00f3n", "\u9f8d"):
            with self.subTest(name=name):
                self.assertEqual(naming.validate_project_name(name), name)

    def test_rejects_empty_and_blank(self):
        for name in ("", "   ", "\t\n"):
            with self.subTest(name=repr(name)):
                with self.assertRaises(ValidationError):
                    naming.validate_project_name(name)

    def test_drops_surrounding_blanks(self):
        self.assertEqual(naming.validate_project_name("  Demo  "), "Demo")

    def test_rejects_non_text(self):
        with self.assertRaises(ValidationError):
            naming.validate_project_name(None)


if __name__ == "__main__":
    unittest.main()
