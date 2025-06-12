import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from codesimulator.config import AppConfig, DEFAULT_APPLICATIONS_JSON_CONTENT
# Assuming path_utils is used by AppConfig for get_resource_path
# from codesimulator.path_utils import get_resource_path

class TestAppConfig(unittest.TestCase):

    def setUp(self):
        self.mock_toga_app = MagicMock()
        # Mock the main_window and dialogs for _display_console_message
        self.mock_toga_app.main_window = MagicMock()
        self.mock_toga_app.main_window.info_dialog = MagicMock()
        self.mock_toga_app.main_window.error_dialog = MagicMock()

        # Patch 'get_resource_path' in the context of the 'codesimulator.config' module,
        # as that's where AppConfig will look for it.
        self.patcher_get_resource_path = patch('codesimulator.config.get_resource_path')
        self.mock_get_resource_path = self.patcher_get_resource_path.start()
        self.mock_get_resource_path.return_value = "mock_resources/applications.json"

        # This setup will run _load_applications_config upon AppConfig instantiation.
        # So, for tests focusing on specific load scenarios, we might need to re-patch/re-init.

    def tearDown(self):
        self.patcher_get_resource_path.stop()

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_applications_success(self, mock_json_load, mock_file_open, mock_os_exists):
        """Test successful loading of applications.json."""
        sample_apps_content = [{"name": "App1", "path_darwin": "/App1.app"}]
        mock_json_load.return_value = sample_apps_content

        app_config = AppConfig(app=self.mock_toga_app) # Instantiation triggers load

        mock_file_open.assert_called_once_with("mock_resources/applications.json", 'r')
        self.assertEqual(app_config.apps, sample_apps_content)
        self.mock_toga_app.main_window.info_dialog.assert_not_called()
        self.mock_toga_app.main_window.error_dialog.assert_not_called()

    @patch('json.dump')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False) # Simulate file not existing
    @patch('builtins.open', new_callable=mock_open)
    def test_load_applications_file_not_found_creates_default(self, mock_file_open, mock_os_exists, mock_os_makedirs, mock_json_dump):
        """Test default applications.json creation if not found."""
        app_config = AppConfig(app=self.mock_toga_app)

        mock_os_makedirs.assert_called_with(os.path.dirname("mock_resources/applications.json"), exist_ok=True)
        mock_file_open.assert_called_with("mock_resources/applications.json", 'w')
        mock_json_dump.assert_called_once_with(DEFAULT_APPLICATIONS_JSON_CONTENT, mock_file_open(), indent=4)
        self.assertEqual(app_config.apps, DEFAULT_APPLICATIONS_JSON_CONTENT)
        self.mock_toga_app.main_window.info_dialog.assert_any_call(
            "applications.json Created",
            "Default applications.json created in resources folder. Please configure it."
        )

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="invalid json data")
    @patch('json.load', side_effect=json.JSONDecodeError("Error", "doc", 0))
    def test_load_applications_invalid_json_uses_empty_list(self, mock_json_load, mock_file_open, mock_os_exists):
        """Test that an empty list is used if applications.json is malformed."""
        app_config = AppConfig(app=self.mock_toga_app)

        self.assertEqual(app_config.apps, [])
        self.mock_toga_app.main_window.error_dialog.assert_any_call(
            "applications.json Error",
            "Error: Malformed JSON in applications.json. Using empty list."
        )

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_applications_not_a_list_uses_empty_list(self, mock_json_load, mock_file_open, mock_os_exists):
        """Test that an empty list is used if root of applications.json is not a list."""
        mock_json_load.return_value = {"not": "a list"} # Simulate JSON object instead of list

        app_config = AppConfig(app=self.mock_toga_app)

        self.assertEqual(app_config.apps, [])
        self.mock_toga_app.main_window.error_dialog.assert_any_call(
            "applications.json Error",
            "Error: applications.json is malformed (should be a list). Using empty list."
        )

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_applications_list_with_non_dict_item_uses_empty_list(self, mock_json_load, mock_file_open, mock_os_exists):
        """Test empty list if applications.json is a list but contains non-dict items."""
        mock_json_load.return_value = [{"name": "App1"}, "not-a-dict"]

        app_config = AppConfig(app=self.mock_toga_app)

        self.assertEqual(app_config.apps, [])
        self.mock_toga_app.main_window.error_dialog.assert_any_call(
            "applications.json Error",
            "Error: applications.json has invalid items (should be list of objects). Using empty list."
        )

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_add_application(self, mock_file_open, mock_json_dump):
        """Test adding an application."""
        # Start with a known state (e.g. default loaded, or empty)
        with patch('os.path.exists', return_value=False): # Simulate no initial file to load default
            app_config = AppConfig(app=self.mock_toga_app)
        self.assertEqual(app_config.apps, DEFAULT_APPLICATIONS_JSON_CONTENT) # Ensure default was loaded

        mock_file_open.reset_mock() # Reset from potential default creation
        mock_json_dump.reset_mock()

        new_app = {"name": "NewApp", "path_darwin": "/New.app"}
        result = app_config.add_application(new_app)
        self.assertTrue(result)
        self.assertIn(new_app, app_config.apps)
        mock_file_open.assert_called_with("mock_resources/applications.json", 'w')
        mock_json_dump.assert_called_with(app_config.apps, mock_file_open(), indent=4)

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_remove_application(self, mock_file_open, mock_json_dump):
        """Test removing an application."""
        initial_apps = [
            {"name": "AppToRemove", "path_darwin": "/ToRemove.app"},
            {"name": "AppToKeep", "path_darwin": "/ToKeep.app"}
        ]
        with patch('os.path.exists', return_value=True), \
             patch('json.load', return_value=initial_apps):
            app_config = AppConfig(app=self.mock_toga_app)
        self.assertEqual(app_config.apps, initial_apps)

        mock_file_open.reset_mock()
        mock_json_dump.reset_mock()

        result = app_config.remove_application("AppToRemove")
        self.assertTrue(result)
        self.assertNotIn({"name": "AppToRemove", "path_darwin": "/ToRemove.app"}, app_config.apps)
        self.assertIn({"name": "AppToKeep", "path_darwin": "/ToKeep.app"}, app_config.apps)
        mock_file_open.assert_called_with("mock_resources/applications.json", 'w')
        mock_json_dump.assert_called_with(app_config.apps, mock_file_open(), indent=4)


if __name__ == '__main__':
    unittest.main()
