"""The two configuration layers and the order in which they are discovered.

These tests never read the real machine configuration. Every case builds its
own temporary files and its own fake environment, because a test that depends
on ~/.config passes here and fails on any other machine, which is exactly the
defect this project claims to fight.
"""

import json
import tempfile
import unittest
from pathlib import Path

from wpipeline import config
from wpipeline.errors import ConfigError, PolicyError


class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write_json(self, name, payload):
        path = self.dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload), encoding="utf-8")
        return path


class TestPolicy(ConfigTestCase):
    def test_loads_the_shipped_policy_without_arguments(self):
        policy = config.load_policy()
        self.assertEqual(policy["project_code"]["length"], 3)

    def test_policy_path_is_relative_to_the_package(self):
        # Not to the working directory: the answer must not depend on where
        # the tool was invoked from.
        self.assertTrue(str(config.POLICY_PATH).endswith("wpipeline/policy/pipeline.json"))
        self.assertTrue(config.POLICY_PATH.is_file())

    def test_missing_policy_raises(self):
        with self.assertRaises(PolicyError):
            config.load_policy(self.dir / "nope.json")

    def test_broken_policy_raises(self):
        path = self.write_json("pipeline.json", "{ not json")
        with self.assertRaises(PolicyError):
            config.load_policy(path)


class TestDiscoveryOrder(ConfigTestCase):
    def setUp(self):
        super().setUp()
        self.env_file = self.write_json(
            "from_env.json", {"schema_version": 1, "roots": {"envroot": "/tmp/env"}}
        )
        self.user_file = self.write_json(
            "from_user.json", {"schema_version": 1, "roots": {"userroot": "/tmp/user"}}
        )

    def test_environment_variable_wins(self):
        loaded = config.load_machine_config(
            env={config.MACHINE_ENV_VAR: str(self.env_file)},
            default_path=self.user_file,
        )
        self.assertEqual(loaded.root_names(), ["envroot"])
        self.assertEqual(loaded.source, config.SOURCE_ENVIRONMENT)
        self.assertIn(config.MACHINE_ENV_VAR, loaded.description)

    def test_user_file_wins_when_no_variable(self):
        loaded = config.load_machine_config(env={}, default_path=self.user_file)
        self.assertEqual(loaded.root_names(), ["userroot"])
        self.assertEqual(loaded.source, config.SOURCE_USER_FILE)
        self.assertIn(str(self.user_file), loaded.description)

    def test_defaults_are_empty_when_nothing_exists(self):
        # The versioned defaults never carry roots: a local path in a public
        # repo is hardcoding that changed address.
        loaded = config.load_machine_config(
            env={}, default_path=self.dir / "absent.json"
        )
        self.assertEqual(loaded.roots, {})
        self.assertEqual(loaded.source, config.SOURCE_DEFAULTS)

    def test_layers_are_not_merged(self):
        # The winning layer wins whole. Nothing from the user file may survive
        # when the environment variable answers.
        loaded = config.load_machine_config(
            env={config.MACHINE_ENV_VAR: str(self.env_file)},
            default_path=self.user_file,
        )
        self.assertNotIn("userroot", loaded.roots)
        self.assertEqual(len(loaded.roots), 1)

    def test_blank_variable_is_treated_as_unset(self):
        loaded = config.load_machine_config(
            env={config.MACHINE_ENV_VAR: "   "}, default_path=self.user_file
        )
        self.assertEqual(loaded.source, config.SOURCE_USER_FILE)

    def test_variable_pointing_at_a_missing_file_is_an_error(self):
        # A broken declaration, not an absent one. Falling through in silence
        # would turn a typo into "all my projects disappeared".
        missing = self.dir / "typo.json"
        with self.assertRaises(ConfigError) as caught:
            config.load_machine_config(
                env={config.MACHINE_ENV_VAR: str(missing)},
                default_path=self.user_file,
            )
        message = str(caught.exception)
        self.assertIn(str(missing), message)
        self.assertIn(config.MACHINE_ENV_VAR, message)


class TestMachineFileShape(ConfigTestCase):
    def load(self, payload):
        path = self.write_json("machine.json", payload)
        return config.load_machine_config(env={}, default_path=path)

    def test_reads_roots_as_paths(self):
        loaded = self.load({"schema_version": 1, "roots": {"main": "/tmp/main"}})
        self.assertEqual(loaded.roots["main"], Path("/tmp/main"))

    def test_expands_the_user_home(self):
        # So that a config file can say ~ and survive a different user name,
        # the same reason the launcher uses $HOME.
        loaded = self.load({"schema_version": 1, "roots": {"internal": "~/projects"}})
        self.assertEqual(loaded.roots["internal"], Path.home() / "projects")

    def test_invalid_json_raises(self):
        with self.assertRaises(ConfigError):
            self.load("{ not json")

    def test_missing_roots_key_raises_with_an_example(self):
        with self.assertRaises(ConfigError) as caught:
            self.load({"schema_version": 1})
        self.assertIn("roots", str(caught.exception))

    def test_roots_must_be_an_object(self):
        with self.assertRaises(ConfigError):
            self.load({"schema_version": 1, "roots": ["/tmp/main"]})

    def test_root_value_must_be_a_non_empty_string(self):
        for bad in ({"main": ""}, {"main": None}, {"main": 5}):
            with self.subTest(roots=bad):
                with self.assertRaises(ConfigError):
                    self.load({"schema_version": 1, "roots": bad})


class TestRequireRoots(ConfigTestCase):
    def test_returns_the_roots_when_there_are_some(self):
        loaded = config.MachineConfig(
            roots={"main": Path("/tmp/main")}, source=config.SOURCE_USER_FILE
        )
        self.assertEqual(config.require_roots(loaded), loaded.roots)

    def test_zero_roots_is_an_instructive_error(self):
        loaded = config.MachineConfig(roots={}, source=config.SOURCE_DEFAULTS)
        with self.assertRaises(ConfigError) as caught:
            config.require_roots(loaded)

        message = str(caught.exception)
        # The message has to carry the exact file to write and content that can
        # be copied off the screen.
        self.assertIn(str(config.MACHINE_CONFIG_PATH), message)
        self.assertIn('"roots"', message)
        self.assertIn(config.MACHINE_ENV_VAR, message)

    def test_the_shipped_example_is_a_placeholder(self):
        # This string lives in a public repo. It must never carry a real path.
        self.assertNotIn(str(Path.home()), config.EXAMPLE_MACHINE_CONFIG)
        self.assertIn("YourVolume", config.EXAMPLE_MACHINE_CONFIG)
        json.loads(config.EXAMPLE_MACHINE_CONFIG)  # and it must be valid JSON


if __name__ == "__main__":
    unittest.main()
