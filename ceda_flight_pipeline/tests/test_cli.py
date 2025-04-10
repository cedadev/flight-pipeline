import unittest
import os
from unittest.mock import patch, mock_open

# Importing the functions to be tested from cli.py
from ceda_flight_pipeline.cli import str2bool


class TestFlightUpdate(unittest.TestCase):

    # Test the conversion function, turnings strings into bools

    def test_str2bool(self):

        self.assertTrue(str2bool("yes"))
        self.assertTrue(str2bool("Y"))
        self.assertTrue(str2bool("1"))
        self.assertFalse(str2bool("no"))
        self.assertFalse(str2bool("false"))

    # Test openConfig() with the correct configuration
    # Mock opening file

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="line0\n/flights-dir\nline2\n/archive\nline4\n",
    )
    @patch.dict(
        os.environ, {"CONFIG_FILE": "dummy_config"}
    )  # Set the CONFIG_FILE env variable
    def test_open_config_success(self, mock_file):

        from ceda_flight_pipeline.cli import openConfig

        root, archive = openConfig()

        # Check if the function correctly reads and returns the expected paths
        self.assertEqual(root, "/flights-dir")
        self.assertEqual(archive, "/archive")

    # Test openConfig() when the config file isn't set up correctly and there aren't enough lines -> triggering an index error
    @patch(
        "builtins.open", new_callable=mock_open, read_data="line0\n/flights-dir\n"
    )  # Only two lines
    @patch.dict(os.environ, {"CONFIG_FILE": "dummy_config"})
    def test_open_config_index_error(self, mock_file):
        from ceda_flight_pipeline.cli import openConfig

        with patch("builtins.print") as mock_print:
            root, archive = openConfig()
        # Check if it returns empty strings as expected
        self.assertEqual((root, archive), ("", ""))

        mock_print.assert_called_once()

    # Test moveOldFiles() when files have to be moved
    def test_move_old_files_move_mode(self):
        commands = []  # initialising empty list where future os commands will be added

        # Capture shell commands by os.system
        def check_cmnds(cmd):
            commands.append(cmd)

        # Creating test files and dirs
        files = ["test.json", "/nested/file2.json"]
        root = "/flights-dir"
        archive = "/archive"

        with patch("os.system", check_cmnds):
            from ceda_flight_pipeline.cli import moveOldFiles

            moveOldFiles(root, archive, files)

        # Expected operations for each test file from move function
        expected = [
            f"mv /flights-dir/test.json /archive/test.json",
            f"mv /flights-dir/file2.json /archive/file2.json",
        ]
        # Check the commands are as expected
        self.assertEqual(commands, expected)

    # Test moveOldFiles() when archive mode is DELETE (files should be deleted)
    def test_move_old_files_delete_mode(self):
        commands = []  # initialising empty list where future os commands will be added

        # Capture shell commands by os.system
        def check_cmnds(cmd):
            commands.append(cmd)

        # Creating test files and dirs
        files = ["test.json", "/nested/file2.json"]
        root = "/flights-dir"
        archive = "DELETE"

        with patch("os.system", check_cmnds):
            from ceda_flight_pipeline.cli import moveOldFiles

            moveOldFiles(root, archive, files)

        # Expected delete operations for each file

        expected = [f"rm /flights-dir/test.json", f"rm /flights-dir/file2.json"]

        self.assertEqual(commands, expected)  # check correct


# test runner
if __name__ == "__main__":
    unittest.main()
