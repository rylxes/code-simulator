import sys
import json
import os
from typing import Dict, List, Optional # Added Optional
from .logging_config import logger
from .path_utils import get_resource_path # Ensure get_resource_path is imported directly if not already

# This DEFAULT_APPS is no longer the direct structure of applications.json
# It can be removed or kept if there's another use for it, but the new
# applications.json will be a list. For now, I'll remove it to avoid confusion.
# DEFAULT_APPS = { ... }


DEFAULT_APPLICATIONS_JSON_CONTENT = [
    {
        "name": "ExampleApp",
        "path_darwin": "/Applications/Example.app", # General path for macOS
        "bundle_id": "com.example.ExampleApp",     # Specific for macOS matching/activation
        "process_name_darwin": "ExampleApp",       # Process name for macOS (if needed by CGWindowList)

        "path_windows": "C:\\Program Files\\Example\\example.exe", # General path for Windows
        "process_name_windows": "example.exe",   # Process name for Windows
        "window_class_windows": "ExampleWindowClass", # Specific for Windows matching

        "path_linux": "/usr/bin/example",          # General path for Linux
        "process_name_linux": "example",           # Process name for Linux
        "window_class_linux": "ExampleWindowClass" # Specific for Linux matching (e.g. WM_CLASS)
    }
]

class AppConfig:
    def __init__(self, app=None): # app is likely a Toga.App instance
        self.app = app
        self.config_path = self._get_applications_config_path()
        # self.platform = sys.platform # platform attribute might still be useful for AppSwitcher
        self.apps: List[Dict] = self._load_applications_config()

    def _display_console_message(self, title: str, message: str, is_error: bool = False):
        """Helper to display messages, Toga specific."""
        logger.info(f"Console message: {title} - {message}")
        if self.app and hasattr(self.app, 'main_window'):
            try:
                if is_error:
                    self.app.main_window.error_dialog(title, message)
                else:
                    self.app.main_window.info_dialog(title, message)
            except Exception as e:
                logger.error(f"Failed to display Toga dialog: {e}")
        else:
            # Fallback if Toga app/main_window is not available (e.g. during tests or early init)
            # This could be a print statement or direct textbox manipulation if available elsewhere.
            # For now, logging is the primary fallback.
            print(f"INFO: {title} - {message}" if not is_error else f"ERROR: {title} - {message}")


    def _get_applications_config_path(self) -> str:
        """Get the path to the applications.json configuration file."""
        # Ensure get_resource_path is available, assuming it's imported at the top of the file
        return get_resource_path(self.app, 'applications.json')

    def _load_applications_config(self) -> List[Dict]:
        """
        Load the applications.json file.
        If not found, creates a default one.
        If found but malformed, logs error and returns empty list.
        """
        if not os.path.exists(self.config_path):
            logger.info(f"applications.json not found at {self.config_path}. Creating default.")
            self._display_console_message("applications.json Created",
                                          f"Default applications.json created in resources folder. Please configure it.")
            return self._create_default_applications_file()

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                logger.error(f"Malformed applications.json: Root is not a list. Path: {self.config_path}")
                self._display_console_message("applications.json Error",
                                              "Error: applications.json is malformed (should be a list). Using empty list.",
                                              is_error=True)
                return []

            for item in data:
                if not isinstance(item, dict):
                    logger.error(f"Malformed applications.json: Contains non-object items in the list. Path: {self.config_path}")
                    self._display_console_message("applications.json Error",
                                                  "Error: applications.json has invalid items (should be list of objects). Using empty list.",
                                                  is_error=True)
                    return []

            logger.info(f"Successfully loaded applications.json from {self.config_path}")
            return data
        except json.JSONDecodeError:
            logger.error(f"Malformed JSON in applications.json at {self.config_path}.")
            self._display_console_message("applications.json Error",
                                          f"Error: Malformed JSON in applications.json. Using empty list.",
                                          is_error=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading applications.json from {self.config_path}: {e}")
            self._display_console_message("applications.json Error",
                                          f"Unexpected error loading applications.json. Using empty list. See logs.",
                                          is_error=True)
            return []

    def _create_default_applications_file(self) -> List[Dict]:
        """Create and save default applications.json file with a list structure."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(DEFAULT_APPLICATIONS_JSON_CONTENT, f, indent=4)
            logger.info(f"Default applications.json created at {self.config_path}")
            return DEFAULT_APPLICATIONS_JSON_CONTENT
        except Exception as e:
            logger.error(f"Error saving default applications.json to {self.config_path}: {e}")
            self._display_console_message("applications.json Error",
                                          f"Could not create default applications.json. See logs.",
                                          is_error=True)
            return [] # Fallback to empty list if creation fails

    def get_applications(self) -> List[Dict]:
        """Get the list of applications."""
        return self.apps

    def _save_applications_config(self) -> bool:
        """Saves the current self.apps list to applications.json"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.apps, f, indent=4)
            logger.info(f"Saved applications configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving applications configuration to {self.config_path}: {e}")
            self._display_console_message("Save Error",
                                          "Failed to save applications.json. Check logs.",
                                          is_error=True)
            return False

    def add_application(self, app_info: Dict) -> bool:
        """Add a new application to the configuration."""
        if not isinstance(app_info, dict) or not app_info.get("name"): # Basic validation
            logger.error(f"Attempted to add invalid application info: {app_info}")
            return False

        # Prevent duplicates by name
        if any(app.get("name") == app_info["name"] for app in self.apps):
            logger.warning(f"Application '{app_info['name']}' already exists. Not adding.")
            self._display_console_message("Add Application", f"Application '{app_info['name']}' already exists.")
            return False

        self.apps.append(app_info)
        return self._save_applications_config()

    def remove_application(self, app_name: str) -> bool:
        """Remove an application from the configuration by name."""
        original_len = len(self.apps)
        self.apps = [app for app in self.apps if app.get("name") != app_name]

        if len(self.apps) < original_len:
            return self._save_applications_config()
        else:
            logger.warning(f"Application '{app_name}' not found for removal.")
            self._display_console_message("Remove Application", f"Application '{app_name}' not found.")
        return False