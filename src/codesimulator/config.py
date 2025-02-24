import sys
import json
import os

from typing import Dict, List
from .logging_config import logger

DEFAULT_APPS = {
    'darwin': {  # macOS
        'applications': [
            {
                'name': 'Google Chrome',
                'process_name': 'Google Chrome',
                'bundle_id': 'com.google.Chrome',
            },
            {
                'name': 'IntelliJ IDEA',
                'process_name': 'IntelliJ IDEA',
                'bundle_id': 'com.jetbrains.intellij',
            },
            {
                'name': 'Sublime Text',
                'process_name': 'Sublime Text',
                'bundle_id': 'com.sublimetext.4',
            }
        ]
    },
    'win32': {  # Windows
        'applications': [
            {
                'name': 'Google Chrome',
                'process_name': 'chrome.exe',
                'window_class': 'Chrome_WidgetWin_1',
            },
            {
                'name': 'IntelliJ IDEA',
                'process_name': 'idea64.exe',
                'window_class': 'SunAwtFrame',
            },
            {
                'name': 'Sublime Text',
                'process_name': 'sublime_text.exe',
                'window_class': 'PX_WINDOW_CLASS',
            }
        ]
    },
    'linux': {  # Linux
        'applications': [
            {
                'name': 'Google Chrome',
                'process_name': 'chrome',
                'window_class': 'Google-chrome',
            },
            {
                'name': 'IntelliJ IDEA',
                'process_name': 'idea.sh',
                'window_class': 'jetbrains-idea',
            },
            {
                'name': 'Sublime Text',
                'process_name': 'sublime_text',
                'window_class': 'sublime_text',
            }
        ]
    }
}


class AppConfig:
    def __init__(self):
        self.config_path = self._get_config_path()
        self.platform = sys.platform
        self.apps = self._load_config()

    def _get_config_path(self) -> str:
        """Get the path to the configuration file."""
        config_dir = os.path.join(os.path.dirname(__file__), 'resources')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        return os.path.join(config_dir, 'applications.json')

    def _load_config(self) -> Dict:
        """Load the configuration file or create default if it doesn't exist."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    if self.platform in config:
                        return config

            # If config doesn't exist or platform not found, use defaults
            return self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading config3: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """Create and save default configuration."""
        config = DEFAULT_APPS
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving default config: {e}")
        return config

    def get_applications(self) -> List[Dict]:
        """Get the list of applications for the current platform."""
        return self.apps.get(self.platform, {}).get('applications', [])

    def add_application(self, app_info: Dict) -> bool:
        """Add a new application to the configuration."""
        try:
            if self.platform not in self.apps:
                self.apps[self.platform] = {'applications': []}

            self.apps[self.platform]['applications'].append(app_info)

            with open(self.config_path, 'w') as f:
                json.dump(self.apps, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error adding application: {e}")
            return False

    def remove_application(self, app_name: str) -> bool:
        """Remove an application from the configuration."""
        try:
            if self.platform in self.apps:
                apps = self.apps[self.platform]['applications']
                self.apps[self.platform]['applications'] = [
                    app for app in apps if app['name'] != app_name
                ]

                with open(self.config_path, 'w') as f:
                    json.dump(self.apps, f, indent=4)
                return True
        except Exception as e:
            logger.error(f"Error removing application: {e}")
        return False