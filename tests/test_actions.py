import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import sys
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from codesimulator.actions import ActionSimulator

DEFAULT_CONFIG_CONTENT = {
    "code": {
        "language": "python",
        "indent_size": 4,
        "max_line_length": 80
    },
    "typing_speed": {
        "min": 0.03,
        "max": 0.07,
        "line_break": [0.5, 1.0],
        "mistake_rate": 0.07
    }
}

class TestActionSimulator(unittest.TestCase):

    def setUp(self):
        self.mock_text_box = MagicMock()
        self.mock_text_box.value = ""
        self.mock_app = MagicMock()

        self.mock_pyautogui_module = MagicMock()
        self.mock_pyautogui_module.size.return_value = (1920, 1080) # Configure .size()
        self.original_pyautogui_in_sys_modules = sys.modules.get('pyautogui')
        sys.modules['pyautogui'] = self.mock_pyautogui_module

        self.patcher_get_resource_path = patch('codesimulator.path_utils.get_resource_path')
        self.mock_get_resource_path = self.patcher_get_resource_path.start()
        self.mock_get_resource_path.return_value = "mock_resources/config.json"

        with patch('codesimulator.actions.AppSwitcher') as self.MockAppSwitcherClass, \
             patch('codesimulator.actions.AppConfig') as self.MockAppConfigClass:
            self.action_simulator = ActionSimulator(self.mock_text_box, self.mock_app)

        if self.original_pyautogui_in_sys_modules is not None:
            sys.modules['pyautogui'] = self.original_pyautogui_in_sys_modules
        elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is self.mock_pyautogui_module:
            del sys.modules['pyautogui']

    def tearDown(self):
        self.patcher_get_resource_path.stop()
        if hasattr(self, 'original_pyautogui_in_sys_modules'):
            if self.original_pyautogui_in_sys_modules is not None:
                sys.modules['pyautogui'] = self.original_pyautogui_in_sys_modules
            elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is self.mock_pyautogui_module:
                del sys.modules['pyautogui']
        if hasattr(self, 'current_test_original_pyautogui'):
            if self.current_test_original_pyautogui is not None:
                sys.modules['pyautogui'] = self.current_test_original_pyautogui
            elif 'pyautogui' in sys.modules: # Check if it's a mock and not the setUp one
                current_pyautogui_in_sys = sys.modules['pyautogui']
                is_mock = isinstance(current_pyautogui_in_sys, MagicMock)
                is_not_setup_mock = current_pyautogui_in_sys != self.mock_pyautogui_module if hasattr(self, 'mock_pyautogui_module') else True
                if is_mock and is_not_setup_mock:
                    del sys.modules['pyautogui']
            if hasattr(self, 'current_test_original_pyautogui'): # ensure delete if set
                 delattr(self, 'current_test_original_pyautogui')


    @patch('json.dump')
    @patch('os.makedirs')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_config_file_not_found_creates_default(self, mock_file_open, mock_os_exists, mock_os_makedirs, mock_json_dump):
        mock_os_exists.return_value = False
        self.mock_get_resource_path.return_value = "mock_resources/new_config.json"
        self.mock_text_box.value = ""

        self.current_test_original_pyautogui = sys.modules.get('pyautogui')
        mock_pyautogui_for_this_test = MagicMock()
        mock_pyautogui_for_this_test.size.return_value = (1920, 1080)
        sys.modules['pyautogui'] = mock_pyautogui_for_this_test

        with patch('codesimulator.actions.AppSwitcher') as MockSwitcher, \
             patch('codesimulator.actions.AppConfig') as MockConfig:
            simulator = ActionSimulator(self.mock_text_box, self.mock_app)

        if self.current_test_original_pyautogui is not None:
            sys.modules['pyautogui'] = self.current_test_original_pyautogui
        elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is mock_pyautogui_for_this_test:
            del sys.modules['pyautogui']

        mock_os_makedirs.assert_called_with(os.path.dirname("mock_resources/new_config.json"), exist_ok=True)
        mock_file_open.assert_any_call("mock_resources/new_config.json", 'w')
        mock_json_dump.assert_called_once()
        args, _ = mock_json_dump.call_args
        dumped_config = args[0]
        self.assertEqual(dumped_config['code']['language'], DEFAULT_CONFIG_CONTENT['code']['language'])
        self.assertEqual(simulator.language, DEFAULT_CONFIG_CONTENT['code']['language'])
        self.assertIn("Default configuration file created at new_config.json", self.mock_text_box.value)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_config_success(self, mock_json_load, mock_file_open, mock_os_exists):
        mock_os_exists.return_value = True
        mock_json_load.return_value = dict(DEFAULT_CONFIG_CONTENT)
        self.mock_text_box.value = ""

        self.current_test_original_pyautogui = sys.modules.get('pyautogui')
        mock_pyautogui_for_this_test = MagicMock()
        mock_pyautogui_for_this_test.size.return_value = (1920, 1080)
        sys.modules['pyautogui'] = mock_pyautogui_for_this_test

        with patch('codesimulator.actions.AppSwitcher'), patch('codesimulator.actions.AppConfig'):
            simulator = ActionSimulator(self.mock_text_box, self.mock_app)

        if self.current_test_original_pyautogui is not None:
            sys.modules['pyautogui'] = self.current_test_original_pyautogui
        elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is mock_pyautogui_for_this_test:
             del sys.modules['pyautogui']

        self.assertEqual(simulator.config, DEFAULT_CONFIG_CONTENT)
        self.assertEqual(simulator.language, "python")

    @patch.object(ActionSimulator, '_setup_default_config') # No wraps here
    @patch('json.load', side_effect=json.JSONDecodeError("Error", "doc", 0))
    @patch('builtins.open', new_callable=mock_open, read_data="invalid json")
    @patch('os.path.exists', return_value=True)
    def test_load_config_invalid_json_uses_defaults(self, mock_os_exists, mock_file_open, mock_json_load, mock_setup_default_config_method):
        self.mock_text_box.value = ""
        self.current_test_original_pyautogui = sys.modules.get('pyautogui')
        mock_pyautogui_for_this_test = MagicMock()
        mock_pyautogui_for_this_test.size.return_value = (1920, 1080)
        sys.modules['pyautogui'] = mock_pyautogui_for_this_test

        with patch('codesimulator.actions.AppSwitcher'), patch('codesimulator.actions.AppConfig'):
            # simulator instance will be created, and its __init__ will call _setup_default_config
            # because _load_config_with_defaults will return None due to JSONDecodeError.
            # The mock_setup_default_config_method will capture this call.
            simulator = ActionSimulator(self.mock_text_box, self.mock_app)

        if self.current_test_original_pyautogui is not None:
            sys.modules['pyautogui'] = self.current_test_original_pyautogui
        elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is mock_pyautogui_for_this_test:
             del sys.modules['pyautogui']

        self.assertIsNone(simulator.config) # config is None
        mock_setup_default_config_method.assert_called_once() # Check if the mocked method was called
        # We can't check simulator.language easily here if _setup_default_config is fully mocked (no wraps)
        # But we trust that if it's called, it does its job. Or we test _setup_default_config separately.
        self.assertIn("Malformed JSON in config.json", self.mock_text_box.value)

    @patch.object(ActionSimulator, '_setup_default_config') # No wraps
    @patch('json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_load_config_missing_critical_keys_uses_defaults(self, mock_os_exists, mock_file_open, mock_json_load, mock_setup_default_config_method):
        config_missing_keys = {"code": {"language": "java"}}
        mock_json_load.return_value = config_missing_keys
        self.mock_text_box.value = ""
        self.current_test_original_pyautogui = sys.modules.get('pyautogui')
        mock_pyautogui_for_this_test = MagicMock()
        mock_pyautogui_for_this_test.size.return_value = (1920, 1080)
        sys.modules['pyautogui'] = mock_pyautogui_for_this_test

        with patch('codesimulator.actions.AppSwitcher'), patch('codesimulator.actions.AppConfig'):
            simulator = ActionSimulator(self.mock_text_box, self.mock_app)

        if self.current_test_original_pyautogui is not None:
            sys.modules['pyautogui'] = self.current_test_original_pyautogui
        elif 'pyautogui' in sys.modules and sys.modules['pyautogui'] is mock_pyautogui_for_this_test:
             del sys.modules['pyautogui']

        self.assertIsNone(simulator.config)
        mock_setup_default_config_method.assert_called_once()
        self.assertIn("Invalid configuration in config.json", self.mock_text_box.value)

    @patch('codesimulator.actions.logger.error')
    @patch('builtins.open', new_callable=mock_open, read_data="line1\nline2\nline3")
    def test_calculate_typing_time_valid_file(self, mock_file_open_method, mock_logger_error_method):
        # self.action_simulator is from setUp, its pyautogui.size() was already handled.
        # We need to ensure self.action_simulator.config is valid for this test,
        # or specifically its self.action_simulator.typing_speed part.
        # The setUp should result in a default config being loaded into self.action_simulator.
        if self.action_simulator.config is None : # If config loading failed in setUp for some reason
            self.action_simulator._setup_default_config() # Manually set defaults
        self.action_simulator.typing_speed = DEFAULT_CONFIG_CONTENT['typing_speed'] # Ensure it for test

        self.mock_text_box.value = ""
        file_path = "dummy.txt"
        expected_total_time = 3.3
        result = asyncio.run(self.action_simulator.calculate_typing_time(file_path))
        self.assertIsNotNone(result)
        self.assertIn('total_time_seconds', result)
        self.assertAlmostEqual(result['total_time_seconds'], expected_total_time, places=2)
        mock_logger_error_method.assert_not_called()
        self.assertIn(f"Estimated typing time: {self.action_simulator._format_time(expected_total_time)}", self.mock_text_box.value)

    @patch('codesimulator.actions.logger.error')
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_calculate_typing_time_file_not_found(self, mock_file_open_method, mock_logger_error_method):
        self.mock_text_box.value = ""
        file_path = "non_existent.txt"
        result = asyncio.run(self.action_simulator.calculate_typing_time(file_path))
        self.assertIsNone(result)
        mock_logger_error_method.assert_called_with(f"File not found for time calculation: {file_path}", exc_info=True)
        self.assertIn(f"Error: File '{os.path.basename(file_path)}' not found for time calculation.", self.mock_text_box.value)

if __name__ == '__main__':
    unittest.main()
