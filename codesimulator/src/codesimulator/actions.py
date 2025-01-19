import asyncio
import logging
import os
import random
import sys
import time
from typing import Optional

import pyautogui

from .app_switcher import AppSwitcher
from .config import AppConfig

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
        self.typing_speed = {
            "min": 0.05,
            "max": 0.15,
            "line_break": (1.0, 2.0),
            "mistake_rate": 0.09,
        }

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
                    # Calculate and show estimated time before starting
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
            with open(file_path, "r") as file:
                lines = file.readlines()

            logger.info(f"Started typing code from {file_path}")
            self.text_box.value += f"Started typing code...\n"

            for line in lines:
                if not self.loop_flag:
                    break

                line = line.rstrip()  # Remove trailing whitespace
                if not line:  # Handle empty lines
                    pyautogui.press("enter")
                    await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
                    continue

                await self._type_line_with_simulation(line)

                # Add a natural pause between lines
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))

        except FileNotFoundError:
            logger.error(f"Code file not found: {file_path}")
            self.text_box.value += "Error: Code file not found\n"
        except Exception as e:
            logger.error(f"Error during code typing: {e}")
            self.text_box.value += f"Error during code typing: {e}\n"

    async def _type_line_with_simulation(self, line: str):
        """Type a single line with realistic simulation of typing behavior."""
        for char in line:
            if not self.loop_flag:
                break

            # Simulate occasional typing mistake
            if random.random() < self.typing_speed["mistake_rate"]:
                await self._simulate_typing_mistake(char)

            # Type the actual character
            pyautogui.write(char)

            # Random delay between keystrokes
            await asyncio.sleep(
                random.uniform(self.typing_speed["min"], self.typing_speed["max"])
            )

        # Press enter at the end of the line
        pyautogui.press("enter")
        logger.info(f"Typed line: {line}")

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