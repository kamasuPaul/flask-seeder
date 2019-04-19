import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from flask import Flask

from flask_seeder import cli, FlaskSeeder
from flask_seeder import Seeder

# This is for mocking os.walk, returns a list with dirs and files
# [ <current dir>, [<subdirs>], [<files in dir>] ]
MOCK_FILES = [
    ["data", ["sub1", "sub2"], []],
    [os.path.join("data", "sub1"), [], ["file1.py", "file2.py"]],
    [os.path.join("data", "sub2"), [], ["file3.py", "file4.py"]],
]

class TestSeedCLI(TestCase):

    def setUp(self):
        self.app = Flask("test")
        self.cli = self.app.test_cli_runner()
        self.seeder = FlaskSeeder()
        self.seeder.init_app(self.app)

    @patch("flask_seeder.cli.os.walk", return_value=MOCK_FILES)
    def test_get_seed_scripts_return_list_of_modules(self, mocked):
        expected_result = [
            os.path.join("data", "sub1", "file1.py"),
            os.path.join("data", "sub1", "file2.py"),
            os.path.join("data", "sub2", "file3.py"),
            os.path.join("data", "sub2", "file4.py"),
        ]

        modules = cli.get_seed_scripts()

        self.assertListEqual(modules, expected_result)

    @patch("flask_seeder.cli.get_seeders")
    def test_seeder_calls_run_method_on_loaded_modules(self, m_get_seeders):
        m_seeder = MagicMock()
        m_get_seeders.return_value = [m_seeder]

        self.cli.invoke(cli.seed_run)

        m_seeder.run.assert_called_once()

    @patch("flask_seeder.cli.get_seed_scripts", return_value=["test"])
    @patch("flask_seeder.cli.get_seeders_from_script")
    def test_get_seeders_return_list_of_seeders(self, m_get_seeders, m_get_scripts):
        m_seeder = MagicMock()
        m_get_seeders.return_value = [m_seeder]
        expected_result = [m_seeder]

        result = cli.get_seeders()

        self.assertListEqual(result, expected_result)

    @patch("flask_seeder.cli.get_seeders")
    def test_seed_list_print_list_of_seeders(self, m_get_seeders):
        m_seeder = MagicMock()
        m_seeder.name = "testseeder"
        m_get_seeders.return_value = [m_seeder]

        result = self.cli.invoke(cli.seed_list)

        self.assertTrue("testseeder" in result.output)

    @patch("flask_seeder.cli.get_seeders")
    def test_seed_run_echo_failed_runs(self, m_get_seeders):
        class TestSeeder(Seeder):
            def run(self):
                raise ValueError()
        m_get_seeders.return_value = [TestSeeder()]

        result = self.cli.invoke(cli.seed_run)

        self.assertTrue("ERROR" in result.output)

    @patch("flask_seeder.cli.get_seeders")
    def test_root_option_with_list(self, m_get_seeders):

        self.cli.invoke(cli.seed_list, args=["--root", "sub1"])

        m_get_seeders.assert_called_once_with(root="sub1")

    @patch("flask_seeder.cli.get_seeders")
    def test_root_option_with_run(self, m_get_seeders):

        self.cli.invoke(cli.seed_run, args=["--root", "sub1"])

        m_get_seeders.assert_called_once_with(root="sub1")

    @patch("flask_seeder.cli.get_seeders")
    def test_run_with_seeder_argument(self, m_get_seeders):
        m_seeder = MagicMock()
        m_seeder.name = "TestSeeder"
        m_get_seeders.return_value = [m_seeder]

        self.cli.invoke(cli.seed_run, args=["TestSeeder"])

        m_seeder.run.assert_called_once()
