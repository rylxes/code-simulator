import asyncio
import os
import random
import time
import sys
import json
from typing import Optional

# PyAutoGUI import will be attempted in _configure_pyautogui
# import pyautogui

from .app_switcher import AppSwitcher
from .config import AppConfig
from .language_formatter import FormatterFactory
from .logging_config import logger
from .mouse import MouseController


class ActionSimulator:
    """Simulates keyboard and mouse actions for code typing simulation."""

    def __init__(self, text_box, app=None):
        self.text_box = text_box
        self.app = app
        self.loop_flag = False
        self.pyautogui_failed = False # Initialize the flag
        self._configure_pyautogui()
        self.app_config = AppConfig(app)
        # Initialize AppSwitcher only if pyautogui is available, as it might be used for window interactions
        # However, AppSwitcher itself doesn't directly import pyautogui, it uses subprocess or platform APIs.
        # So, it should be safe to initialize regardless of pyautogui status for now.
        # If AppSwitcher's methods start failing due to lack of GUI interaction capabilities (indirectly),
        # then this might need reconsideration. For now, the task is specific about pyautogui dependent actions.
        self.app_switcher = AppSwitcher(self.app_config)
        self.formatter_factory = FormatterFactory()
        self.formatter = None
        self.mouse_controller = MouseController()
        self.simulation_mode = "Hybrid"  # default mode

        # Load configuration or set up defaults
        self.config = self._load_config_with_defaults() # Renamed for clarity
        if self.config is None: # Indicates error with existing or inability to create default
            self._setup_default_config()
            # Message to user is handled in _load_config_with_defaults or _create_default_config
        else:
            self._setup_from_config() # Uses self.config

        # Get list of code files from 'resources/code'
        self.code_files = self._get_code_files()
        self.current_code_index = 0

        self.original_indentations = {}

    def _setup_from_config(self):
        # This method now assumes self.config is valid (not None)
        # as __init__ handles the None case by calling _setup_default_config.
        try:
            code_config = self.config.get('code', {}) # self.config should be populated
            self.language = code_config.get('language', 'python')
            self.indent_size = code_config.get('indent_size', 4)
            self.max_line_length = code_config.get('max_line_length', 80)
            typing_config = self.config.get('typing_speed', {})
            self.typing_speed = {
                'min': typing_config.get('min', 0.03),
                'max': typing_config.get('max', 0.07),
                'line_break': tuple(typing_config.get('line_break', [0.5, 1.0])),
                'mistake_rate': typing_config.get('mistake_rate', 0.07)
            }
            logger.info("Successfully configured simulation settings from config file.")
        except Exception as e:
            logger.error(f"Error setting up configuration from presumably valid config: {e}. Falling back to defaults.")
            # This case might happen if config is structured but has subtle issues not caught by _load_config_with_defaults
            self._setup_default_config() # Fallback

    def _setup_default_config(self):
        logger.warning("Using hardcoded default configuration settings.")
        self.text_box.value += "⚠️ Using hardcoded default configuration. Check logs or Configuration tab.\n"
        self.language = 'python'
        self.indent_size = 4
        self.max_line_length = 80
        self.typing_speed = {
            'min': 0.03,
            'max': 0.07,
            'line_break': (0.5, 1.0),
            'mistake_rate': 0.07,
        }

    def _get_config_path(self) -> str:
        from .path_utils import get_resource_path
        # This function just returns the path, existence check will be in _load_config_with_defaults
        return get_resource_path(self.app, 'config.json')

    def _create_default_config(self, config_path: str) -> dict:
        default_settings = {
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
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(default_settings, f, indent=2)
            logger.info(f"Created default configuration file at {config_path}")
            self.text_box.value += f"ℹ️ Default configuration file created at {os.path.basename(config_path)}. You can customize it in the Configuration tab or directly in the file.\n"
            return default_settings
        except Exception as e:
            logger.error(f"Could not create default config file at {config_path}: {e}")
            self.text_box.value += f"❌ Error: Could not create default config at {os.path.basename(config_path)}. Using hardcoded defaults. See logs.\n"
            return None # Indicates failure to create

    def _get_code_files(self) -> list:
        """Return a list of .txt files from the 'resources/code' directory."""
        from .path_utils import get_resource_path
        code_dir = get_resource_path(self.app, 'code')
        if os.path.isdir(code_dir):
            files = [os.path.join(code_dir, f) for f in os.listdir(code_dir) if f.endswith(".txt")]
            if not files:
                logger.warning(f"No .txt files found in {code_dir}")
            return files
        else:
            logger.warning(f"Code directory not found: {code_dir}")
            return []

    def _load_config_with_defaults(self) -> Optional[dict]:
        config_path = self._get_config_path()

        if not os.path.exists(config_path):
            logger.info(f"Config file not found at {config_path}. Creating a default one.")
            self.text_box.value += f"ℹ️ Configuration file (config.json) not found. Creating a default one.\n"
            return self._create_default_config(config_path)

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Validate structure and types
            if not isinstance(config, dict):
                raise ValueError("Config is not a JSON object.")

            code_config = config.get('code')
            if not isinstance(code_config, dict):
                raise ValueError("'code' section is missing or not an object.")
            if not isinstance(code_config.get('language'), str):
                raise ValueError("'language' in 'code' is missing or not a string.")
            if not isinstance(code_config.get('indent_size'), int):
                raise ValueError("'indent_size' in 'code' is missing or not an integer.")
            if not isinstance(code_config.get('max_line_length'), int):
                raise ValueError("'max_line_length' in 'code' is missing or not an integer.")

            typing_config = config.get('typing_speed')
            if not isinstance(typing_config, dict):
                raise ValueError("'typing_speed' section is missing or not an object.")
            min_speed = typing_config.get('min')
            if not isinstance(min_speed, (float, int)):
                raise ValueError("'min' in 'typing_speed' is missing or not a number.")
            max_speed = typing_config.get('max')
            if not isinstance(max_speed, (float, int)):
                raise ValueError("'max' in 'typing_speed' is missing or not a number.")
            line_break = typing_config.get('line_break')
            if not (isinstance(line_break, list) and len(line_break) == 2 and
                    all(isinstance(x, (float, int)) for x in line_break)):
                raise ValueError("'line_break' in 'typing_speed' must be a list of two numbers.")
            mistake_rate = typing_config.get('mistake_rate')
            if not isinstance(mistake_rate, (float, int)):
                raise ValueError("'mistake_rate' in 'typing_speed' is missing or not a number.")

            logger.info(f"Successfully loaded and validated configuration from {config_path}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in config file {config_path}: {e}")
            self.text_box.value += f"❌ Error: Malformed JSON in {os.path.basename(config_path)}. Using default settings. Please check the file or use the Configuration tab.\n"
            return None # Signal to use default config
        except ValueError as e: # For custom validation errors
            logger.error(f"Invalid configuration in {config_path}: {e}")
            self.text_box.value += f"❌ Error: Invalid configuration in {os.path.basename(config_path)}: {e}. Using default settings. Please check the file or use the Configuration tab.\n"
            return None # Signal to use default config
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
            self.text_box.value += f"❌ Error loading {os.path.basename(config_path)}. Using default settings. See logs.\n"
            return None # Signal to use default config

    def load_config(self): # This seems to be an unused/alternative method. I'll leave it for now.
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')
            logger.info(f"Loading config from: {config_path}")
            with open(config_path, "r") as f:
                config = json.load(f)
                code_config = config.get('code', {})
                self.language = code_config.get("language", "unknown")
                self.indent_size = code_config.get("indent_size", 4)
                self.max_line_length = code_config.get("max_line_length", 80)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.language = "unknown"
            self.indent_size = 4
            self.max_line_length = 80

    async def simulate_command_tab(self):
        """Simulate pressing Command+Tab to switch applications."""
        if self.pyautogui_failed:
            message = "⚠️ PyAutoGUI failed. Command+Tab simulation disabled.\n"
            if self.text_box.value.count(message) < 2: self.text_box.value += message
            logger.warning("Attempted simulate_command_tab when PyAutoGUI is not available.")
            return

        # Ensure pyautogui is imported if not already globally due to deferred import
        global pyautogui
        if 'pyautogui' not in globals():
            logger.error("PyAutoGUI module not loaded for simulate_command_tab.") # Should not happen if configure passed
            return

        try:
            if sys.platform == 'darwin':
                pyautogui.hotkey('command', 'tab')
            elif sys.platform == 'win32':
                pyautogui.hotkey('alt', 'tab')
            else:  # Linux
                pyautogui.hotkey('alt', 'tab')

            logger.info("Pressed Command+Tab / Alt+Tab")
            await asyncio.sleep(0.5)
        except Exception as e: # Catch pyautogui specific exceptions if possible
            logger.error(f"Error simulating Command+Tab: {e}")
            self.text_box.value += f"Error during Command+Tab: {e}\n"


    def _configure_pyautogui(self):
        self.pyautogui_failed = False
        global pyautogui # Make it assignable at global scope within this module
        try:
            import pyautogui as pgui # Import with an alias to manage scope
            pyautogui = pgui # Assign to global name 'pyautogui' if import successful
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1 # Adjusted default pause
            logger.info(f"PyAutoGUI initialized. Screen size: {pyautogui.size()}. FAILSAFE: {pyautogui.FAILSAFE}, PAUSE: {pyautogui.PAUSE}")
        except Exception as e: # Catching a broad exception as PyAutoGUI can raise various things
            self.pyautogui_failed = True
            logger.error(f"PyAutoGUI initialization failed: {e}", exc_info=True)
            error_message = (
                "❌ CRITICAL: PyAutoGUI failed to initialize!\n"
                "Typing and mouse simulation will NOT work.\n"
            )
            if sys.platform == 'darwin':
                error_message += "Suggestion (macOS): Check 'System Settings > Privacy & Security > Accessibility'. Ensure this app (or your terminal/IDE if running from source) has permissions.\n"
            elif sys.platform == 'linux':
                error_message += "Suggestion (Linux): You might be missing dependencies such as 'scrot', 'python3-tk', 'python3-dev', or Xlib libraries (e.g., libx11-dev, libxtst-dev, libxinerama-dev, libxcursor-dev, libxi-dev).\nTry: sudo apt-get install scrot python3-tk python3-dev libx11-dev libxtst-dev libxinerama-dev libxcursor-dev libxi-dev\n"
            else:
                error_message += "Please ensure your environment supports GUI automation.\n"

            # Add to textbox only if not already present to avoid repetition
            if error_message not in self.text_box.value:
                self.text_box.value += error_message



    def get_next_code_file(self) -> Optional[str]:
        """Return the next code file in sequence (cycling through available files)."""
        if self.code_files:
            file_path = self.code_files[self.current_code_index]
            self.current_code_index = (self.current_code_index + 1) % len(self.code_files)
            return file_path
        return None

    def _split_file_into_chunks(self, file_path: str, chunk_size: int = 50) -> list:
        """Split the file into chunks of at most 'chunk_size' lines."""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
            if len(lines) <= chunk_size:
                return [lines]
            chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
            logger.info(f"Split file {file_path} into {len(chunks)} chunks")
            return chunks
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}", exc_info=True)
            self.text_box.value += f"❌ Error reading file: '{os.path.basename(file_path)}' not found.\n"
            return []
        except (IOError, OSError) as e:
            logger.error(f"IO/OS Error reading file {file_path}: {e}", exc_info=True)
            self.text_box.value += f"❌ Error reading file '{os.path.basename(file_path)}': {e}. Check permissions and path.\n"
            return []

    async def calculate_typing_time(self, file_path: str) -> Optional[dict]:
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
            total_chars = sum(len(line.rstrip()) for line in lines) # Exclude \n from char count
            total_lines = len(lines)
            empty_lines = sum(1 for line in lines if not line.strip())
            non_empty_lines = total_lines - empty_lines

            avg_char_time = (self.typing_speed["min"] + self.typing_speed["max"]) / 2
            char_typing_time = total_chars * avg_char_time

            expected_mistakes = int(total_chars * self.typing_speed["mistake_rate"])
            mistake_time = expected_mistakes * (0.2 + 0.1)

            avg_line_break = sum(self.typing_speed["line_break"]) / 2
            line_break_time = non_empty_lines * avg_line_break
            empty_line_time = empty_lines * (avg_line_break * 0.5)

            total_time = char_typing_time + mistake_time + line_break_time + empty_line_time

            timing_details = {
                "total_time_seconds": round(total_time, 2),
                "total_time_formatted": self._format_time(total_time),
                "breakdown": {
                    "characters": {"count": total_chars, "time_seconds": round(char_typing_time, 2)},
                    "lines": {"total": total_lines, "empty": empty_lines, "non_empty": non_empty_lines,
                              "time_seconds": round(line_break_time + empty_line_time, 2)},
                    "expected_mistakes": {"count": expected_mistakes, "time_seconds": round(mistake_time, 2)},
                    "typing_speed": {"chars_per_second": round(1 / avg_char_time, 2),
                                     "avg_pause_between_lines": round(avg_line_break, 2)},
                },
            }
            logger.info(f"Estimated typing time: {timing_details['total_time_formatted']}")
            self.text_box.value += (
                f"Estimated typing time: {timing_details['total_time_formatted']}\n"
                f"Total characters: {total_chars}\n"
                f"Total lines: {total_lines}\n"
                f"Expected mistakes: {expected_mistakes}\n"
            )
            return timing_details

        except FileNotFoundError:
            logger.error(f"File not found for time calculation: {file_path}", exc_info=True)
            self.text_box.value += f"❌ Error: File '{os.path.basename(file_path)}' not found for time calculation.\n"
            return None
        except (IOError, OSError) as e:
            logger.error(f"IO/OS Error reading file for time calculation {file_path}: {e}", exc_info=True)
            self.text_box.value += f"❌ Error reading file '{os.path.basename(file_path)}' for time calculation: {e}.\n"
            return None
        except Exception as e: # Catch any other unexpected errors
            logger.error(f"Unexpected error calculating typing time for {file_path}: {e}", exc_info=True)
            self.text_box.value += f"❌ Unexpected error calculating typing time for '{os.path.basename(file_path)}': {e}.\n"
            return None

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)
        if hours > 0:
            return f"{hours}h {minutes}m {remaining_seconds}s"
        elif minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"

    # Replace the simulate_typing method in actions.py (around line 210):

    async def simulate_typing(self, file_path: Optional[str] = None):
        """Simulate typing code from a file."""
        logger.debug(f"simulate_typing called with file_path: {file_path}")

        if self.simulation_mode == "Tab Switching Only":
            self.text_box.value += "Tab switching only mode selected. Skipping typing simulation...\n"
            return
        elif self.simulation_mode in ["Typing Only", "Hybrid"]:
            # Validate file path
            if not file_path:
                logger.error("No file path provided for typing simulation")
                self.text_box.value += "❌ Error: No file path provided for typing simulation.\n"
                return

            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                self.text_box.value += f"❌ Error: File not found: {file_path}\n"
                return

            logger.info(f"Simulating typing with file: {file_path}")
            self.text_box.value += f"Typing from file: {os.path.basename(file_path)}\n"

            # Split file into chunks and type
            chunks = self._split_file_into_chunks(file_path, chunk_size=50)
            for i, chunk in enumerate(chunks):
                if not self.loop_flag:
                    break
                chunk_text = "".join(chunk)
                await self._simulate_code_typing_from_lines(chunk_text, i)
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
        else:
            self.text_box.value += "Unknown simulation mode selected.\n"

    async def _simulate_code_typing_from_lines(self, text: str, chunk_index: int):
        if self.pyautogui_failed: # Check at higher level if possible
            # Message already displayed by _type_line_with_simulation or its children
            return

        lines = text.splitlines(keepends=True)
        original_indents = {i: len(line) - len(line.lstrip()) for i, line in enumerate(lines)}
        self.text_box.value += f"Typing chunk {chunk_index + 1}...\n"
        for i, line in enumerate(lines):
            if not self.loop_flag:
                break
            line = " " * original_indents.get(i, 0) + line.strip()
            if not line: # Empty line after stripping
                if self.pyautogui_failed: return # Redundant check, but safe
                global pyautogui
                if 'pyautogui' not in globals(): return
                pyautogui.press("enter")
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
                continue
            await self._type_line_with_simulation(line, i)
            await asyncio.sleep(random.uniform(*self.typing_speed["line_break"])) # Pause between lines

    async def _type_line_with_simulation(self, line: str, line_num: int):
        if self.pyautogui_failed:
            message = "⚠️ PyAutoGUI failed. Typing simulation disabled.\n"
            if self.text_box.value.count(message) < 2: self.text_box.value += message
            logger.warning("Attempted _type_line_with_simulation when PyAutoGUI is not available.")
            return
        global pyautogui
        if 'pyautogui' not in globals(): return


        if self.formatter:
            line = self.formatter.format_line(line)
        for char in line:
            if not self.loop_flag:
                break
            if random.random() < self.typing_speed["mistake_rate"]:
                await self._simulate_typing_mistake(char) # Already checks pyautogui_failed
            self._type_character(char) # Already checks pyautogui_failed
            await asyncio.sleep(random.uniform(self.typing_speed["min"], self.typing_speed["max"]))

        if not self.pyautogui_failed and 'pyautogui' in globals():
            pyautogui.press("enter")
            logger.info(f"Typed line: {line}")

    async def _simulate_typing_mistake(self, correct_char: str):
        if self.pyautogui_failed:
            # Message will be shown by parent or _type_character
            return
        global pyautogui
        if 'pyautogui' not in globals(): return

        wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
        pyautogui.write(wrong_char)
        await asyncio.sleep(0.2)
        pyautogui.press("backspace")
        await asyncio.sleep(0.1)

    def _type_character(self, char: str):
        if self.pyautogui_failed:
            message = "⚠️ PyAutoGUI failed. Character typing disabled.\n"
            # Reduce verbosity, main message in _configure_pyautogui and _type_line_with_simulation
            # if self.text_box.value.count(message) < 2: self.text_box.value += message
            # logger.warning("Attempted _type_character when PyAutoGUI is not available.")
            return
        global pyautogui
        if 'pyautogui' not in globals(): return

        if char == "\t":
            pyautogui.press("tab")
        elif char == "\n": # Should be handled by line break logic, but as a safeguard
            pyautogui.press("enter")
        else:
            pyautogui.write(char)

    def switch_window(self):
        # This method uses AppSwitcher, which might use OS commands, not directly pyautogui for focus.
        # However, if future AppSwitcher versions use pyautogui, the flag would be relevant.
        # For now, no pyautogui_failed check seems necessary here unless AppSwitcher itself uses it.
        app = self.app_switcher.get_random_running_app()
        if app:
            if self.app_switcher.focus_application(app):
                self.text_box.value += f"Switched to {app['name']}\n" # Message from successful switch
                logger.info(f"Switched to {app['name']}")
            else:
                self.text_box.value += f"Failed to switch to {app['name']}\n" # Message from failed switch
                logger.error(f"Failed to switch to {app['name']}")
        else:
            self.text_box.value += "No configured applications running to switch to.\n" # More informative
            logger.warning("No configured applications running")

    async def _simulate_random_actions(self):
        if self.pyautogui_failed:
            # This is a top-level coordinator for random actions.
            # Individual actions will also check, but good to stop early.
            message = "⚠️ PyAutoGUI failed. Random mouse/keyboard actions disabled.\n"
            if self.text_box.value.count(message) < 2: self.text_box.value += message
            logger.warning("Attempted _simulate_random_actions when PyAutoGUI is not available.")
            return

        while self.loop_flag:
            actions_to_perform = []
            # Check pyautogui_failed before adding actions that depend on it
            if not self.pyautogui_failed:
                actions_to_perform.extend([
                    self._random_cursor_move,
                    self._random_scroll,
                    self._middle_click,
                ])
            # _window_switch_action does not directly depend on pyautogui, so it can be added.
            actions_to_perform.append(self._window_switch_action)

            random.shuffle(actions_to_perform) # Shuffle to make it more random

            for action in actions_to_perform:
                if not self.loop_flag:
                    break
                await action() # Individual actions will perform their own pyautogui_failed checks
            await asyncio.sleep(random.uniform(0.3, 0.7))

    async def _random_cursor_move(self):
        if self.pyautogui_failed: return
        global pyautogui
        if 'pyautogui' not in globals(): return
        x = random.randint(100, pyautogui.size().width - 100) # Use actual screen size
        y = random.randint(100, pyautogui.size().height - 100)
        pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.7))
        logger.info(f"Moved cursor to ({x}, {y})")

    async def _random_scroll(self):
        if self.pyautogui_failed: return
        global pyautogui
        if 'pyautogui' not in globals(): return
        scroll_amount = random.randint(-5, 5) # More realistic scroll units
        pyautogui.scroll(scroll_amount)
        logger.info(f"Scrolled {scroll_amount} units")
        await asyncio.sleep(random.uniform(0.3, 0.6))
        # Reducing subsequent moves to keep focus on scroll
        # pyautogui.move(100, 50, duration=0.5)
        # logger.info("Moved mouse relatively by (100, 50).")
        # await asyncio.sleep(0.5)
        # pyautogui.move(-50, -25, duration=0.5)
        # logger.info("Moved mouse relatively by (-50, -25).")
        # await asyncio.sleep(0.5)

    async def _middle_click(self):
        if self.pyautogui_failed: return
        global pyautogui
        if 'pyautogui' not in globals(): return
        if random.random() < 0.3:
            pyautogui.click(button="middle")
            logger.info("Middle clicked")

    async def _window_switch_action(self):
        # This action itself doesn't use pyautogui, but is part of the simulation loop
        if random.random() < 0.2: # Keep existing probability
            self.switch_window() # switch_window has its own checks if it were to use pyautogui
            await asyncio.sleep(0.5) # Pause after potential switch

    async def _cleanup_simulation(self):
        # No specific pyautogui actions here, but good for consistency if needed later
        await asyncio.sleep(0.5)

    def _handle_simulation_end(self):
        self.loop_flag = False
        self.mouse_controller.stop()
        self.text_box.value += "Simulation ended\n"
        logger.info("Simulation ended")

    async def simulate_mouse_and_command_tab(self, duration=10):
        """
        Simulate mouse movements and Command+Tab key combination for window switching.

        Args:
            duration (int): The approximate duration in seconds for the simulation
        """
        if not self.loop_flag:
            return

        self.text_box.value += "🖱️ Simulating mouse movements and Command+Tab...\n"
        logger.info("Starting mouse and Command+Tab simulation")

        start_time = time.time()

        try:
            if not self.pyautogui_failed: # Only start mouse controller if pyautogui is fine
                self.mouse_controller.start(min_interval=1.0, max_interval=3.0)
            else:
                logger.warning("PyAutoGUI failed, mouse controller will not be started for simulate_mouse_and_command_tab.")
                # Display a message if this specific simulation is attempted with failed pyautogui
                message = "⚠️ PyAutoGUI failed. Mouse simulation part of Command+Tab sequence is disabled.\n"
                if self.text_box.value.count(message) < 2: self.text_box.value += message


            # Perform a sequence of mouse movements and command+tab presses
            while self.loop_flag and (time.time() - start_time < duration):
                if not self.pyautogui_failed:
                    # Random mouse movements
                    for _ in range(random.randint(1, 3)):
                        if not self.loop_flag:
                            break
                        await self._random_cursor_move() # This will check pyautogui_failed
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                else: # If pyautogui failed, just sleep instead of mouse moves
                    await asyncio.sleep(random.uniform(0.5, 1.5))


                # Occasional Command+Tab (this also checks pyautogui_failed)
                if random.random() < 0.7:  # 70% chance to do Command+Tab
                    await self.simulate_command_tab()

                # Add a small pause
                await asyncio.sleep(random.uniform(1.0, 2.0))

        finally:
            # Make sure to stop the mouse controller if it was started
            if self.mouse_controller.is_running: # Assuming is_running attribute or similar
                 self.mouse_controller.stop()
            logger.info("Mouse and Command+Tab simulation completed")