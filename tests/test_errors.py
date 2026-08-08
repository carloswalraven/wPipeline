"""The error contract: everything the package raises is one base class.

The CLI catches WPipelineError and nothing else, so any exception that does not
descend from it would escape as a traceback. That is what these tests guard.
"""

import unittest

from wpipeline import errors


class TestErrorHierarchy(unittest.TestCase):
    def test_every_public_error_descends_from_the_base(self):
        names = [
            name
            for name in dir(errors)
            if not name.startswith("_") and name.endswith("Error")
        ]
        # Guards against the module being emptied or renamed without notice.
        self.assertGreater(len(names), 1)

        for name in names:
            with self.subTest(error=name):
                error = getattr(errors, name)
                self.assertTrue(issubclass(error, errors.WPipelineError))

    def test_the_base_is_a_plain_exception(self):
        self.assertTrue(issubclass(errors.WPipelineError, Exception))

    def test_certainty_errors_are_grouped(self):
        # Reading tolerates these; writing must not. Grouping them under one
        # parent is what lets create-project refuse the whole family at once.
        for error in (
            errors.ProjectExistsError,
            errors.PathConflictError,
            errors.CorruptProjectFileError,
        ):
            with self.subTest(error=error.__name__):
                self.assertTrue(issubclass(error, errors.SourceOfTruthError))

    def test_the_message_survives_the_raise(self):
        # The CLI prints str(exception) directly, so the message has to be
        # carried by the exception and not assembled at print time.
        try:
            raise errors.ValidationError("code must be 3 letters")
        except errors.WPipelineError as exc:
            self.assertEqual(str(exc), "code must be 3 letters")


if __name__ == "__main__":
    unittest.main()
