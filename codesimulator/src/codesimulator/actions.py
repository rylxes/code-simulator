import asyncio
import logging
import os
import random
import sys
import json
from typing import Optional

import pyautogui

from .app_switcher import AppSwitcher
from .config import AppConfig
from .language_formatter import FormatterFactory

logger = logging.getLogger(__name__)


class ActionSimulator:
    """Simulates keyboard and mouse actions for code typing simulation."""

    def __init__(self, text_box):
        """Initialize the action simulator."""
        self.text_box = text_box
        self.loop_flag = False
        self._configure_pyautogui()
        self.app_config = AppConfig()
        self.app_switcher = AppSwitcher(self.app_config)
        self.formatter_factory = FormatterFactory()
        self.formatter = None

        # Load configuration
        self.config = self._load_config()
        self._setup_from_config()

        # Keep track of the original indentation for each line
        self.original_indentations = {}

    def _setup_from_config(self):
        """Set up instance variables from loaded configuration."""
        try:
            # Set up code formatting settings
            code_config = self.config.get('code', {})
            self.language = code_config.get('language', 'python')
            self.indent_size = code_config.get('indent_size', 4)
            self.max_line_length = code_config.get('max_line_length', 80)

            # Set up typing speed settings
            typing_config = self.config.get('typing_speed', {})
            self.typing_speed = {
                'min': typing_config.get('min', 0.03),
                'max': typing_config.get('max', 0.07),
                'line_break': tuple(typing_config.get('line_break', [0.5, 1.0])),
                'mistake_rate': typing_config.get('mistake_rate', 0.07)
            }

            logger.info("Successfully configured simulation settings")
        except Exception as e:
            logger.error(f"Error setting up configuration: {e}")
            # Use default values if configuration fails
            self._setup_default_config()

    def _setup_default_config(self):
        """Set up default configuration if loading fails."""
        logger.warning("Using default configuration settings")
        self.language = 'python'
        self.indent_size = 4
        self.max_line_length = 80
        self.typing_speed = {
            'min': 0.03,
            'max': 0.07,
            'line_break': (0.5, 1.0),
            'mistake_rate': 0.07
        }

    def _get_config_path(self) -> str:
        """Get the path to the config.json file in resources directory."""
        config_path = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')
        if not os.path.exists(config_path):
            logger.error(f"Config file not found at {config_path}")
            raise FileNotFoundError(f"Config file not found at {config_path}")
        return config_path

    def _load_config(self) -> dict:
        """Load configuration from config.json file."""
        try:
            with open(self._get_config_path(), 'r') as f:
                config = json.load(f)
                logger.info("Successfully loaded configuration")
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config1: {e}")
            raise

    def load_config(self):
        """Load configuration from the config file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')
            logger.info(f"Loading config from: {config_path}")
            with open(config_path, "r") as f:
                config = json.load(f)
                code_config = config.get('code', {})
                self.language = code_config.get("language", "unknown")
                self.indent_size = code_config.get("indent_size", 4)
                self.max_line_length = code_config.get("max_line_length", 80)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            self.language = "unknown"
            self.indent_size = 4
            self.max_line_length = 80
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.language = "unknown"
            self.indent_size = 4
            self.max_line_length = 80

    def _configure_pyautogui(self):
        """Configure PyAutoGUI settings."""
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

    async def calculate_typing_time(self, file_path: str) -> dict:
        """
        Calculate estimated time to type the code based on configuration.

        Returns:
            dict: Contains estimated time in seconds and detailed breakdown
        """
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()

            total_chars = sum(len(line.rstrip()) for line in lines)
            total_lines = len(lines)
            empty_lines = sum(1 for line in lines if not line.strip())
            non_empty_lines = total_lines - empty_lines

            # Calculate timing components
            avg_char_time = (self.typing_speed["min"] + self.typing_speed["max"]) / 2
            char_typing_time = total_chars * avg_char_time

            # Calculate mistake time
            expected_mistakes = int(total_chars * self.typing_speed["mistake_rate"])
            mistake_time = expected_mistakes * (
                    0.2 + 0.1
            )  # 0.2s pause + 0.1s correction

            # Calculate line break time
            avg_line_break = sum(self.typing_speed["line_break"]) / 2
            line_break_time = non_empty_lines * avg_line_break

            # Empty lines take less time
            empty_line_time = empty_lines * (avg_line_break * 0.5)

            # Total estimated time
            total_time = char_typing_time + mistake_time + line_break_time + empty_line_time

            # Create detailed breakdown
            timing_details = {
                "total_time_seconds": round(total_time, 2),
                "total_time_formatted": self._format_time(total_time),
                "breakdown": {
                    "characters": {
                        "count": total_chars,
                        "time_seconds": round(char_typing_time, 2),
                    },
                    "lines": {
                        "total": total_lines,
                        "empty": empty_lines,
                        "non_empty": non_empty_lines,
                        "time_seconds": round(line_break_time + empty_line_time, 2),
                    },
                    "expected_mistakes": {
                        "count": expected_mistakes,
                        "time_seconds": round(mistake_time, 2),
                    },
                    "typing_speed": {
                        "chars_per_second": round(1 / avg_char_time, 2),
                        "avg_pause_between_lines": round(avg_line_break, 2),
                    },
                },
            }

            # Log the estimate
            logger.info(f"Estimated typing time: {timing_details['total_time_formatted']}")
            self.text_box.value += (
                f"Estimated typing time: {timing_details['total_time_formatted']}\n"
                f"Total characters: {total_chars}\n"
                f"Total lines: {total_lines}\n"
                f"Expected mistakes: {expected_mistakes}\n"
            )

            return timing_details

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            self.text_box.value += f"Error: File not found: {file_path}\n"
            return None
        except Exception as e:
            logger.error(f"Error calculating typing time: {e}")
            self.text_box.value += f"Error calculating typing time: {e}\n"
            return None

    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time string."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        remaining_seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {remaining_seconds}s"
        elif minutes > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{remaining_seconds}s"

    async def simulate_typing(self, file_path: Optional[str] = None):
        """Main simulation method."""
        try:
            await self._perform_initial_setup()

            # If file_path is provided, simulate typing from file
            if file_path:
                # Load configuration and create formatter based on the specified language
                self.load_config()
                self.formatter = self.formatter_factory.create_formatter(
                    self.language, self.indent_size
                )

                # Calculate and show estimated time before starting
                timing_details = await self.calculate_typing_time(file_path)
                if timing_details:
                    # Give user a moment to read the estimate
                    await asyncio.sleep(2)
                await self._simulate_code_typing(file_path)
            else:
                # Try to find a default code file
                default_file = self._get_default_code_file()
                if default_file:
                    # Load configuration and create formatter based on the specified language
                    self.load_config()
                    self.formatter = self.formatter_factory.create_formatter(
                        self.language, self.indent_size
                    )

                    timing_details = await self.calculate_typing_time(default_file)
                    if timing_details:
                        # Give user a moment to read the estimate
                        await asyncio.sleep(2)
                    await self._simulate_code_typing(default_file)
                else:
                    # Fall back to random actions if no code file is found
                    await self._simulate_random_actions()

            await self._cleanup_simulation()
        except asyncio.CancelledError:
            logger.info("Simulation cancelled")
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
        finally:
            self._handle_simulation_end()

    def _get_default_code_file(self) -> Optional[str]:
        """Get the path to the default code file in resources."""
        try:
            resources_dir = os.path.join(os.path.dirname(__file__), "resources")
            code_files = [f for f in os.listdir(resources_dir) if f.endswith(".txt")]
            if code_files:
                return os.path.join(resources_dir, random.choice(code_files))
        except Exception as e:
            logger.error(f"Error finding code file: {e}")
        return None

    async def _perform_initial_setup(self):
        """Perform initial simulation setup."""
        self.switch_window()
        await asyncio.sleep(1)
        self.click_center_screen()
        await asyncio.sleep(0.5)

    def switch_window(self, reverse: bool = False):
        """Switch to a configured application."""
        try:
            self.text_box.value += "Switching application...\n"

            # Get a random running application from our configured list
            app = self.app_switcher.get_random_running_app()

            if app:
                if self.app_switcher.focus_application(app):
                    self.text_box.value += f"Switched to {app['name']}\n"
                    logger.info(f"Switched to {app['name']}")
                else:
                    self.text_box.value += f"Failed to switch to {app['name']}\n"
                    logger.error(f"Failed to switch to {app['name']}")
            else:
                self.text_box.value += "No configured applications running\n"
                logger.warning("No configured applications running")

                # Fall back to default window switching if no configured apps are available
                if sys.platform == "darwin":
                    self._mac_window_switch(reverse)
                else:
                    self._default_window_switch(reverse)

        except Exception as e:
            logger.error(f"Error switching windows: {e}")
            self.text_box.value += f"Error switching windows: {e}\n"

    def _mac_window_switch(self, reverse: bool):
        """Handle MacOS window switching."""
        keys = ["command", "shift", "tab"] if reverse else ["command", "tab"]
        pyautogui.hotkey(*keys)
        logger.info("Switched window using Command+Tab")

    def _default_window_switch(self, reverse: bool):
        """Handle default window switching."""
        keys = ["ctrl", "shift", "tab"] if reverse else ["ctrl", "tab"]
        pyautogui.hotkey(*keys)
        logger.info("Switched window using Ctrl+Tab")

    def click_center_screen(self):
        """Click at the center of the screen."""
        try:
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2)
            self.text_box.value += "Clicked at screen center\n"
            logger.info("Clicked at screen center")
        except Exception as e:
            logger.error(f"Error clicking center screen: {e}")

    async def _simulate_code_typing(self, file_path: str):
        """Simulate typing code from a file with realistic timing and occasional mistakes."""
        try:
            # Create a formatter based on the configured language
            self.formatter = self.formatter_factory.create_formatter(
                self.language, self.indent_size
            )

            with open(file_path, "r") as file:
                lines = file.readlines()

            # Store original indentations
            self.original_indentations = {
                i: len(line) - len(line.lstrip()) for i, line in enumerate(lines)
            }

            logger.info(f"Started typing code from {file_path}")
            self.text_box.value += f"Started typing code...\n"

            for i, line in enumerate(lines):
                if not self.loop_flag:
                    break

                # Use original indentation
                line = " " * self.original_indentations[i] + line.strip()

                if not line:
                    pyautogui.press("enter")
                    await asyncio.sleep(
                        random.uniform(*self.typing_speed["line_break"])
                    )
                    continue

                await self._type_line_with_simulation(line, i)
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))

        except FileNotFoundError:
            logger.error(f"Code file not found: {file_path}")
            self.text_box.value += "Error: Code file not found\n"
        except Exception as e:
            logger.error(f"Error during code typing: {e}")
            self.text_box.value += f"Error during code typing: {e}\n"

    async def _type_line_with_simulation(self, line: str, line_num: int):
        """Type a single line with formatting and realistic simulation."""

        # Use the language-specific formatter if available
        if self.formatter:
            line = self.formatter.format_line(line)

        # Remove any leading/trailing whitespace (important for accurate typing)
        line = line.strip()

        # Wrap Long Lines (if necessary)
        if len(line) > self.max_line_length:
            await self._wrap_long_line(line, line_num)
            return

        # Handle Comments
        if "//" in line:
            line = line.split("//")[0] + " //" + line.split("//")[1].strip()
        elif "#" in line:  # Python comments
            line = line.split("#")[0] + " #" + line.split("#")[1].strip()

        # Typing Simulation
        # Restore original indentation
        line = " " * self.original_indentations[line_num] + line
        for char in line:
            if not self.loop_flag:
                break

            if random.random() < self.typing_speed["mistake_rate"]:
                await self._simulate_typing_mistake(char)

            self._type_character(char)
            await asyncio.sleep(
                random.uniform(self.typing_speed["min"], self.typing_speed["max"])
            )

        pyautogui.press("enter")
        logger.info(f"Typed line: {line}")

    async def _wrap_long_line(self, line: str, line_num: int, depth: int = 0):
        """
        Wrap a long line at a suitable breaking point, taking into account
        the current indentation level and language-specific formatting.

        Args:
            line: The line to wrap
            line_num: The line number being processed
            depth: Current recursion depth (default: 0)
        """
        # Prevent infinite recursion
        if depth > 10:  # Maximum reasonable number of line wraps
            logger.warning(f"Maximum line wrap depth reached for line {line_num}")
            await self._type_line_with_simulation(line, line_num)
            return

        current_indent = self.formatter.indent_style * self.formatter.indent_level

        # If line is within limit, type it directly
        if len(line) <= self.max_line_length:
            await self._type_line_with_simulation(line, line_num)
            return

        # Find appropriate break points
        break_points = [
            ('(', ')'),
            (',', None),
            (' ', None)
        ]

        break_point = -1
        for start, end in break_points:
            if end:
                # For matched pairs like parentheses
                open_pos = line.rfind(start, 0, self.max_line_length)
                if open_pos != -1:
                    corresponding_close = line.find(end, open_pos)
                    if corresponding_close != -1 and corresponding_close < self.max_line_length:
                        break_point = corresponding_close
                        break
            else:
                # For single characters like comma or space
                pos = line.rfind(start, 0, self.max_line_length)
                if pos != -1:
                    break_point = pos
                    break

        if break_point != -1:
            # Split and handle the line parts
            first_part = line[:break_point + 1].rstrip()
            second_part = current_indent + line[break_point + 1:].lstrip()

            # Type first part
            await self._type_line_with_simulation(first_part, line_num)

            # Recursively handle second part with increased depth
            await self._wrap_long_line(second_part, line_num, depth + 1)
        else:
            # If no good break point found, force break at max length
            logger.warning(f"No suitable break point found for line {line_num}, forcing break")
            first_part = line[:self.max_line_length]
            second_part = current_indent + line[self.max_line_length:].lstrip()

            await self._type_line_with_simulation(first_part, line_num)
            await self._wrap_long_line(second_part, line_num, depth + 1)

    def _type_character(self, char: str):
        """Type a single character or handle special characters."""
        if char == "\t":
            pyautogui.press("tab")
        elif char == "\n":
            pyautogui.press("enter")
        else:
            pyautogui.write(char)

    async def _simulate_typing_mistake(self, correct_char: str):
        """Simulate a typing mistake and correction."""
        # Type a wrong character
        wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
        pyautogui.write(wrong_char)
        await asyncio.sleep(0.2)  # Slight pause before correction

        # Correct the mistake
        pyautogui.press("backspace")
        await asyncio.sleep(0.1)

    async def _simulate_random_actions(self):
        """Simulate random mouse and keyboard actions."""
        while self.loop_flag:
            actions = [
                self._random_cursor_move,
                self._random_scroll,
                self._middle_click,
                self._window_switch_action,
            ]
            for action in actions:
                if not self.loop_flag:
                    break
                await action()
            await asyncio.sleep(random.uniform(0.3, 0.7))
    async def _random_cursor_move(self):
        """Perform random cursor movement."""
        x = random.randint(100, 1000)
        y = random.randint(100, 1000)
        pyautogui.moveTo(x, y, duration=0.5)
        logger.info(f"Moved cursor to ({x}, {y})")

    async def _random_scroll(self):
        """Perform random scrolling."""
        scroll_amount = random.randint(-100, 100)
        pyautogui.scroll(scroll_amount)
        logger.info(f"Scrolled {scroll_amount}")

        await asyncio.sleep(0.5)

        # Relative Mouse Move (Example values)
        pyautogui.move(100, 50, duration=0.5)  # Move right 100, down 50
        logger.info("Moved mouse relatively by (100, 50).")
        await asyncio.sleep(0.5)

        # Another Relative Mouse Move (Example values)
        pyautogui.move(-50, -25, duration=0.5)  # Move left 50, up 25
        logger.info("Moved mouse relatively by (-50, -25).")
        await asyncio.sleep(0.5)

    async def _middle_click(self):
        """Perform middle click."""
        if random.random() < 0.3:
            pyautogui.click(button="middle")
            logger.info("Middle clicked")

    async def _window_switch_action(self):
        """Perform window switching action."""
        if random.random() < 0.2:
            self.switch_window()
            await asyncio.sleep(0.5)
            self.switch_window(reverse=True)

    async def _cleanup_simulation(self):
        """Clean up after simulation."""
        self.switch_window(reverse=True)
        await asyncio.sleep(0.5)

    def _handle_simulation_end(self):
        """Handle simulation end state."""
        self.loop_flag = False
        self.text_box.value += "Simulation ended\n"
        logger.info("Simulation ended")