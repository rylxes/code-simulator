import asyncio
import os
import random
import sys
import json
from typing import Optional

import pyautogui

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
        self._configure_pyautogui()
        self.app_config = AppConfig(app)
        self.app_switcher = AppSwitcher(self.app_config)
        self.formatter_factory = FormatterFactory()
        self.formatter = None
        self.mouse_controller = MouseController()
        self.simulation_mode = "Hybrid"  # default mode

        self.config = self._load_config()
        self._setup_from_config()

        # Get list of code files from 'resources/code'
        self.code_files = self._get_code_files()
        self.current_code_index = 0

        self.original_indentations = {}

    def _setup_from_config(self):
        try:
            code_config = self.config.get('code', {})
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
            logger.info("Successfully configured simulation settings")
        except Exception as e:
            logger.error(f"Error setting up configuration: {e}")
            self._setup_default_config()

    def _setup_default_config(self):
        logger.warning("Using default configuration settings")
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
        config_path = get_resource_path(self.app, 'config.json')
        if not os.path.exists(config_path):
            logger.error(f"Config file not found at {config_path}")
            raise FileNotFoundError(f"Config file not found at {config_path}")
        return config_path

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

    def _load_config(self) -> dict:
        try:
            with open(self._get_config_path(), 'r') as f:
                config = json.load(f)
                logger.info("Successfully loaded configuration")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise

    def load_config(self):
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

    def _configure_pyautogui(self):
        try:
            import pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            logger.info(f"PyAutoGUI initialized. Screen size: {pyautogui.size()}")
        except Exception as e:
            logger.error(f"Failed to initialize PyAutoGUI: {e}")
            self.text_box.value += f"⚠️ Warning: Failed to initialize PyAutoGUI: {e}\n"



    def get_next_code_file(self) -> Optional[str]:
        """Return the next code file in sequence (cycling through available files)."""
        if self.code_files:
            file_path = self.code_files[self.current_code_index]
            self.current_code_index = (self.current_code_index + 1) % len(self.code_files)
            return file_path
        return None

    def _split_file_into_chunks(self, file_path: str, chunk_size: int = 50) -> list:
        """Split the file into chunks of at most 'chunk_size' lines."""
        with open(file_path, "r") as f:
            lines = f.readlines()
        if len(lines) <= chunk_size:
            return [lines]
        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        logger.info(f"Split file {file_path} into {len(chunks)} chunks")
        return chunks

    async def calculate_typing_time(self, file_path: str) -> dict:
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
            total_chars = sum(len(line.rstrip()) for line in lines)
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
            logger.error(f"File not found: {file_path}")
            self.text_box.value += f"Error: File not found: {file_path}\n"
            return None
        except Exception as e:
            logger.error(f"Error calculating typing time: {e}")
            self.text_box.value += f"Error calculating typing time: {e}\n"
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

    async def simulate_typing(self, file_path: Optional[str] = None):
        if self.simulation_mode == "Tab Switching Only":
            self.text_box.value += "Tab switching only mode selected. Skipping typing simulation...\n"
            return
        elif self.simulation_mode in ["Typing Only", "Hybrid"]:
            # Split file into chunks if long
            chunks = self._split_file_into_chunks(file_path, chunk_size=50)
            for i, chunk in enumerate(chunks):
                chunk_text = "".join(chunk)
                await self._simulate_code_typing_from_lines(chunk_text, i)
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
        else:
            self.text_box.value += "Unknown simulation mode selected.\n"

    async def _simulate_code_typing_from_lines(self, text: str, chunk_index: int):
        lines = text.splitlines(keepends=True)
        original_indents = {i: len(line) - len(line.lstrip()) for i, line in enumerate(lines)}
        self.text_box.value += f"Typing chunk {chunk_index + 1}...\n"
        for i, line in enumerate(lines):
            if not self.loop_flag:
                break
            line = " " * original_indents.get(i, 0) + line.strip()
            if not line:
                pyautogui.press("enter")
                await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))
                continue
            await self._type_line_with_simulation(line, i)
            await asyncio.sleep(random.uniform(*self.typing_speed["line_break"]))

    async def _type_line_with_simulation(self, line: str, line_num: int):
        if self.formatter:
            line = self.formatter.format_line(line)
        for char in line:
            if not self.loop_flag:
                break
            if random.random() < self.typing_speed["mistake_rate"]:
                await self._simulate_typing_mistake(char)
            self._type_character(char)
            await asyncio.sleep(random.uniform(self.typing_speed["min"], self.typing_speed["max"]))
        pyautogui.press("enter")
        logger.info(f"Typed line: {line}")

    async def _simulate_typing_mistake(self, correct_char: str):
        wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")
        pyautogui.write(wrong_char)
        await asyncio.sleep(0.2)
        pyautogui.press("backspace")
        await asyncio.sleep(0.1)

    def _type_character(self, char: str):
        if char == "\t":
            pyautogui.press("tab")
        elif char == "\n":
            pyautogui.press("enter")
        else:
            pyautogui.write(char)

    def switch_window(self):
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

    async def _simulate_random_actions(self):
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
        x = random.randint(100, 1000)
        y = random.randint(100, 1000)
        pyautogui.moveTo(x, y, duration=0.5)
        logger.info(f"Moved cursor to ({x}, {y})")

    async def _random_scroll(self):
        scroll_amount = random.randint(-100, 100)
        pyautogui.scroll(scroll_amount)
        logger.info(f"Scrolled {scroll_amount}")
        await asyncio.sleep(0.5)
        pyautogui.move(100, 50, duration=0.5)
        logger.info("Moved mouse relatively by (100, 50).")
        await asyncio.sleep(0.5)
        pyautogui.move(-50, -25, duration=0.5)
        logger.info("Moved mouse relatively by (-50, -25).")
        await asyncio.sleep(0.5)

    async def _middle_click(self):
        if random.random() < 0.3:
            pyautogui.click(button="middle")
            logger.info("Middle clicked")

    async def _window_switch_action(self):
        if random.random() < 0.2:
            self.switch_window()
            await asyncio.sleep(0.5)

    async def _cleanup_simulation(self):
        await asyncio.sleep(0.5)

    def _handle_simulation_end(self):
        self.loop_flag = False
        self.mouse_controller.stop()
        self.text_box.value += "Simulation ended\n"
        logger.info("Simulation ended")