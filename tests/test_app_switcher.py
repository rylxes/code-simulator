import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from codesimulator.app_switcher import AppSwitcher
from codesimulator.config import AppConfig # Used for spec for mock_app_config

# Define sample app configurations for testing
CONFIGURED_APPS_SAMPLE = [
    {"name": "App1", "bundle_id": "com.app1.osx", "process_name_darwin": "App1",
     "window_class_windows": "App1WindowClass", "process_name_windows": "app1.exe",
     "window_class_linux": "app1_linux_class", "process_name_linux": "app1_linux"},
    {"name": "App2", "bundle_id": "com.app2.osx", "process_name_darwin": "App2",
     "window_class_windows": "App2WindowClass", "process_name_windows": "app2.exe",
     "window_class_linux": "app2_linux_class", "process_name_linux": "app2_linux"},
    {"name": "NoPlatformSpecificsApp", "name_generic": "App3"}
]

class TestAppSwitcher(unittest.TestCase):

    def setUp(self):
        self.mock_app_config = MagicMock(spec=AppConfig)

        self.original_sys_platform = sys.platform
        # Store original modules that might be replaced
        self.original_modules = {
            'Quartz': sys.modules.get('Quartz'),
            'win32gui': sys.modules.get('win32gui'),
            'win32process': sys.modules.get('win32process'),
            'Xlib': sys.modules.get('Xlib'),
            'Xlib.display': sys.modules.get('Xlib.display')
        }

        # Mock the modules themselves
        sys.modules['Quartz'] = MagicMock()
        sys.modules['win32gui'] = MagicMock()
        sys.modules['win32process'] = MagicMock()

        # For Xlib, mock parent and then its attribute/submodule
        mock_xlib_parent = MagicMock()
        sys.modules['Xlib'] = mock_xlib_parent
        sys.modules['Xlib.display'] = MagicMock()
        # Ensure that if AppSwitcher does 'import Xlib.display' and then 'Xlib.display.Display()' it works
        mock_xlib_parent.display = sys.modules['Xlib.display']
        # If AppSwitcher also uses Xlib.X (e.g. Xatom), mock it too
        sys.modules['Xlib.X'] = MagicMock()
        mock_xlib_parent.X = sys.modules['Xlib.X']


        # Temporarily set a platform for initial AppSwitcher setup, tests can override
        # This ensures AppSwitcher.__init__ doesn't fail on the actual test runner platform
        # if that platform's libraries aren't installed.
        sys.platform = 'linux' # Default to linux for initial setup, as it was causing issues
        self.app_switcher = AppSwitcher(config=self.mock_app_config)
        # AppSwitcher's _setup_platform_handler is called in __init__

    def tearDown(self):
        sys.platform = self.original_sys_platform
        # Restore original modules
        for name, original_module in self.original_modules.items():
            if original_module:
                sys.modules[name] = original_module
            elif name in sys.modules: # If it was added by setUp and not there originally
                # Check if it's one of our mocks before deleting, to be safe
                if isinstance(sys.modules[name], MagicMock):
                    del sys.modules[name]
        # Clean up Xlib parent if it was added and isn't the original
        if self.original_modules.get('Xlib') is None and 'Xlib' in sys.modules and isinstance(sys.modules['Xlib'], MagicMock):
            del sys.modules['Xlib']


    def test_get_random_app_none_configured(self):
        self.mock_app_config.get_applications.return_value = []
        # Platform doesn't matter if no apps are configured
        self.assertIsNone(self.app_switcher.get_random_running_app())

    @patch.object(AppSwitcher, '_get_running_applications_macos')
    def test_get_random_app_one_running_macos(self, mock_get_running_macos):
        sys.platform = 'darwin'
        self.app_switcher.platform = 'darwin'
        # Ensure AppSwitcher._quartz is set to the mock from sys.modules
        self.app_switcher._quartz = sys.modules['Quartz']
        self.app_switcher._setup_platform_handler() # Call to re-initialize platform specifics like self._quartz

        mock_get_running_macos.return_value = [CONFIGURED_APPS_SAMPLE[0]]
        self.mock_app_config.get_applications.return_value = CONFIGURED_APPS_SAMPLE

        running_app = self.app_switcher.get_random_running_app()
        self.assertEqual(running_app, CONFIGURED_APPS_SAMPLE[0])
        mock_get_running_macos.assert_called_once()

    @patch.object(AppSwitcher, '_get_running_applications_windows')
    def test_get_random_app_one_running_windows(self, mock_get_running_windows):
        sys.platform = 'win32'
        self.app_switcher.platform = 'win32'
        self.app_switcher._win32gui = sys.modules['win32gui']
        self.app_switcher._win32process = sys.modules['win32process']
        self.app_switcher._setup_platform_handler()

        mock_get_running_windows.return_value = [CONFIGURED_APPS_SAMPLE[1]]
        self.mock_app_config.get_applications.return_value = CONFIGURED_APPS_SAMPLE

        running_app = self.app_switcher.get_random_running_app()
        self.assertEqual(running_app, CONFIGURED_APPS_SAMPLE[1])
        mock_get_running_windows.assert_called_once()

    @patch.object(AppSwitcher, '_get_running_applications_linux')
    def test_get_random_app_none_running_linux(self, mock_get_running_linux):
        sys.platform = 'linux'
        self.app_switcher.platform = 'linux'
        self.app_switcher._display = sys.modules['Xlib.display'].Display() # Ensure _display is set with mock
        self.app_switcher._setup_platform_handler()

        mock_get_running_linux.return_value = []
        self.mock_app_config.get_applications.return_value = CONFIGURED_APPS_SAMPLE

        self.assertIsNone(self.app_switcher.get_random_running_app())
        mock_get_running_linux.assert_called_once()

    @patch('subprocess.run')
    def test_focus_application_darwin_by_bundle_id(self, mock_subprocess_run):
        sys.platform = 'darwin'
        self.app_switcher.platform = 'darwin'
        self.app_switcher._quartz = sys.modules['Quartz']
        self.app_switcher._setup_platform_handler()

        app_info = CONFIGURED_APPS_SAMPLE[0]
        result = self.app_switcher.focus_application(app_info)

        self.assertTrue(result)
        expected_command = ['osascript', '-e', f'tell application id "{app_info["bundle_id"]}" to activate']
        mock_subprocess_run.assert_called_once_with(expected_command, check=True, capture_output=True, text=True)

    @patch('subprocess.run')
    def test_focus_application_darwin_by_name(self, mock_subprocess_run):
        sys.platform = 'darwin'
        self.app_switcher.platform = 'darwin'
        self.app_switcher._quartz = sys.modules['Quartz']
        self.app_switcher._setup_platform_handler()

        app_info = {"name": "TestAppNoBundle", "path_darwin":"/Test.app"}
        result = self.app_switcher.focus_application(app_info)

        self.assertTrue(result)
        expected_command = ['osascript', '-e', f'tell application "{app_info["name"]}" to activate']
        mock_subprocess_run.assert_called_once_with(expected_command, check=True, capture_output=True, text=True)

    def test_focus_application_windows(self):
        sys.platform = 'win32'
        self.app_switcher.platform = 'win32'
        self.app_switcher._win32gui = sys.modules['win32gui']
        self.app_switcher._win32process = sys.modules['win32process']
        # _setup_platform_handler has already been called in setUp for the default platform,
        # for win32, it will try to use the mocked win32gui and win32process from sys.modules
        self.app_switcher._setup_platform_handler()


        app_info = CONFIGURED_APPS_SAMPLE[0]

        def mock_enum_windows(callback, param_class_name):
            callback(123, param_class_name)
            return None

        self.app_switcher._win32gui.EnumWindows.side_effect = mock_enum_windows
        self.app_switcher._win32gui.IsWindowVisible.return_value = True
        self.app_switcher._win32gui.GetClassName.return_value = app_info['window_class_windows']

        result = self.app_switcher.focus_application(app_info)

        self.assertTrue(result)
        self.app_switcher._win32gui.EnumWindows.assert_called_once()
        self.app_switcher._win32gui.SetForegroundWindow.assert_called_with(123)

    @patch('subprocess.run')
    def test_focus_application_linux_by_class(self, mock_subprocess_run):
        sys.platform = 'linux'
        self.app_switcher.platform = 'linux'
        self.app_switcher._display = sys.modules['Xlib.display'].Display()
        self.app_switcher._setup_platform_handler()

        app_info = CONFIGURED_APPS_SAMPLE[0]
        result = self.app_switcher.focus_application(app_info)

        self.assertTrue(result)
        expected_command = ['wmctrl', '-x', '-a', app_info['window_class_linux'].split()[0]]
        mock_subprocess_run.assert_called_once_with(expected_command, check=True, capture_output=True, text=True)

    @patch('subprocess.run')
    def test_focus_application_linux_by_name(self, mock_subprocess_run):
        sys.platform = 'linux'
        self.app_switcher.platform = 'linux'
        self.app_switcher._display = sys.modules['Xlib.display'].Display()
        self.app_switcher._setup_platform_handler()

        app_info = {"name": "TestAppLinuxNameOnly"}
        result = self.app_switcher.focus_application(app_info)

        self.assertTrue(result)
        expected_command = ['wmctrl', '-a', app_info['name']]
        mock_subprocess_run.assert_called_once_with(expected_command, check=True, capture_output=True, text=True)

if __name__ == '__main__':
    unittest.main()
