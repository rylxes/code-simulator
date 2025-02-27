import asyncio
import os
import tempfile
import platform
import subprocess
import sys
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.colors import rgb
from .actions import ActionSimulator
from .key_handler import GlobalKeyHandler
from .logging_config import get_log_path, setup_file_logging, logger
from .path_utils import log_environment_info, get_log_path

log_environment_info()


class CodeSimulator(toga.App):
    def __init__(self):
        super().__init__(
            formal_name="Code Simulator",
            app_id="com.example.codesimulator"
        )
        # Store a manually selected file (if any)
        self.selected_file = None

    async def show_debug_info(self, widget):

        # Get system information
        info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Python Version": platform.python_version(),
            "App Directory": os.path.dirname(os.path.abspath(__file__)),
            "Current Directory": os.getcwd(),
            "Log File": get_log_path(),
            "Is Packaged": getattr(sys, 'frozen', False),
            "Executable": sys.executable
        }

        # Display in text box
        self.text_box.value = "--- Debug Information ---\n\n"
        for key, value in info.items():
            self.text_box.value += f"{key}: {value}\n"

        # Log detailed info for troubleshooting
        log_environment_info()

        self.text_box.value += "\nDetailed debug information has been logged to the log file.\n"

    async def view_console_logs(self, widget):
        """View recent console output (for macOS/Linux only)"""
        try:
            if platform.system() == "Darwin":  # macOS
                # Get last 50 lines from system log for this app
                process = subprocess.Popen(
                    ["log", "show", "--predicate", "process == 'Code Simulator'", "--last", "1h"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(timeout=5)

                if stdout:
                    self.text_box.value = "Recent Console Logs:\n\n" + stdout
                else:
                    self.text_box.value = "No recent console logs found.\n"
                    if stderr:
                        self.text_box.value += f"Error: {stderr}\n"
            else:
                self.text_box.value = "Console log viewing only supported on macOS."
        except Exception as e:
            self.text_box.value = f"Error viewing console logs: {e}"

    async def view_logs(self, widget):


        # Ensure file logging is set up
        setup_file_logging()

        # Get log path
        log_path = get_log_path()

        # Clear text box
        self.text_box.value = "Log Information\n"
        self.text_box.value += "=============\n\n"
        self.text_box.value += f"Log file location: {log_path}\n\n"

        # Write a test log message
        logger.info("Test log message from View Logs button")

        # Check if log file exists now
        if not os.path.exists(log_path):
            self.text_box.value += f"❌ Log file still not found after write attempt!\n\n"

            # Try to create a simple text file in the same directory to test permissions
            try:
                log_dir = os.path.dirname(log_path)
                test_file_path = os.path.join(log_dir, "test_write.txt")
                with open(test_file_path, 'w') as f:
                    f.write("Test write")
                self.text_box.value += f"✓ Successfully created test file at: {test_file_path}\n"
                os.remove(test_file_path)  # Clean up
            except Exception as e:
                self.text_box.value += f"❌ Could not write test file: {e}\n"
                self.text_box.value += "This suggests a permissions issue or the directory doesn't exist\n"

            # Print environment variables to help debug
            self.text_box.value += "\nEnvironment Information:\n"
            self.text_box.value += f"Working directory: {os.getcwd()}\n"
            self.text_box.value += f"Home directory: {os.path.expanduser('~')}\n"
            self.text_box.value += f"App directory: {os.path.dirname(__file__)}\n"
            self.text_box.value += f"Python executable: {sys.executable}\n"
            self.text_box.value += f"Is packaged: {getattr(sys, 'frozen', False)}\n"

            # Suggest a location for logs
            self.text_box.value += "\nTry looking for logs in these locations:\n"
            self.text_box.value += f"1. {os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')}\n"
            self.text_box.value += f"2. {tempfile.gettempdir()}\n"

            return

        # Display file stats
        file_size = os.path.getsize(log_path)
        last_modified = os.path.getmtime(log_path)
        import datetime
        mod_time = datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')

        self.text_box.value += f"Log file size: {file_size} bytes\n"
        self.text_box.value += f"Last modified: {mod_time}\n\n"

        # Read and display log content
        try:
            with open(log_path, 'r') as f:
                # For larger files, just get the last part
                if file_size > 10000:
                    self.text_box.value += f"Log file is large. Showing last portion...\n\n"
                    f.seek(max(0, file_size - 10000))
                    # Skip potentially incomplete first line
                    f.readline()
                    content = f.read()
                else:
                    content = f.read()

            # Display content
            self.text_box.value += "Log Content:\n"
            self.text_box.value += "===========\n\n"
            self.text_box.value += content

        except Exception as e:
            self.text_box.value += f"❌ Error reading log file: {e}\n"

    def startup(self):
        # Ensure logging is set up
        from .logging_config import setup_file_logging
        setup_file_logging()

        # Continue with normal startup
        self.setup_ui()
        self.setup_components()
        logger.info("Application started successfully.")

    def setup_ui(self):
        # Create a modern color scheme
        self.colors = {
            'primary': rgb(60, 120, 200),  # Blue
            'accent': rgb(60, 180, 100),  # Green
            'danger': rgb(220, 70, 70),  # Red
            'background': rgb(250, 250, 252),  # Off-white
            'card': rgb(255, 255, 255),  # White
            'text': rgb(50, 50, 50),  # Dark grey
            'text_light': rgb(120, 120, 120)  # Light grey
        }

        # Main box with column layout
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Title header
        header = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color=self.colors['primary']))
        title = toga.Label(
            "Code Simulator",
            style=Pack(
                font_size=24,
                font_weight="bold",
                padding=5,
                color=rgb(255, 255, 255),
                text_align=CENTER
            )
        )
        subtitle = toga.Label(
            "Select mode and code file, then start simulation",
            style=Pack(
                font_size=14,
                padding=(0, 5, 5, 5),
                color=rgb(220, 220, 220),
                text_align=CENTER
            )
        )

        header.add(title)
        header.add(subtitle)
        main_box.add(header)

        # Content container with two columns
        content = toga.Box(style=Pack(direction=ROW, padding=10))

        # Left column - Controls
        left_column = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=1))

        # Mode selection
        mode_label = toga.Label(
            "Simulation Mode:",
            style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
        )
        self.simulation_modes = ["Typing Only", "Tab Switching Only", "Hybrid"]
        self.mode_selector = toga.Selection(
            items=self.simulation_modes,
            value=self.simulation_modes[2],
            style=Pack(padding=(0, 0, 20, 0))
        )
        # Add View Logs button
        view_logs_button = toga.Button(
            "View Logs",
            on_press=self.view_logs,
            style=Pack(padding=5, background_color=self.colors['accent'], color=rgb(255, 255, 255))
        )
        debug_info_button = toga.Button(
            "Debug Info",
            on_press=self.show_debug_info,
            style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
        )

        # Add Console Logs button
        console_logs_button = toga.Button(
            "View Console Logs",
            on_press=self.view_console_logs,
            style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
        )
        left_column.add(console_logs_button)
        left_column.add(debug_info_button)
        left_column.add(view_logs_button)
        left_column.add(mode_label)
        left_column.add(self.mode_selector)

        # File selection
        file_label = toga.Label(
            "Selected File:",
            style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
        )
        self.file_display = toga.Label(
            "Using default resources/code files",
            style=Pack(padding=(0, 0, 10, 0), color=self.colors['text_light'])
        )
        choose_file_button = toga.Button(
            "Choose File",
            on_press=self.choose_file,
            style=Pack(padding=5, background_color=self.colors['accent'], color=rgb(255, 255, 255))
        )
        left_column.add(file_label)
        left_column.add(self.file_display)
        left_column.add(choose_file_button)

        # Action buttons
        button_box = toga.Box(style=Pack(direction=ROW, padding=(20, 0, 10, 0)))
        self.start_button = toga.Button(
            "Start Simulation",
            on_press=self.start_simulation,
            style=Pack(padding=5, background_color=self.colors['primary'], color=rgb(255, 255, 255))
        )
        self.stop_button = toga.Button(
            "Stop Simulation",
            on_press=self.stop_simulation,
            style=Pack(padding=5, background_color=self.colors['danger'], color=rgb(255, 255, 255)),
            enabled=False
        )
        button_box.add(self.start_button)
        button_box.add(toga.Box(style=Pack(flex=1)))  # Spacer
        button_box.add(self.stop_button)
        left_column.add(button_box)

        # Information box
        info_box = toga.Box(style=Pack(direction=COLUMN, padding=(20, 0, 0, 0)))
        info_label = toga.Label(
            "Keyboard Shortcuts:",
            style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
        )
        info_text = toga.Label(
            "⌘+S: Start Simulation\n⌘+X: Stop Simulation",
            style=Pack(color=self.colors['text_light'])
        )
        info_box.add(info_label)
        info_box.add(info_text)
        left_column.add(info_box)

        # Right column - Output
        right_column = toga.Box(style=Pack(direction=COLUMN, padding=10, flex=2))
        output_label = toga.Label(
            "Simulation Log:",
            style=Pack(padding=(0, 0, 5, 0), font_weight="bold")
        )
        self.text_box = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, background_color=rgb(245, 245, 250))
        )
        right_column.add(output_label)
        right_column.add(self.text_box)

        # Add columns to content
        content.add(left_column)
        content.add(right_column)

        # Add content to main box
        main_box.add(content)

        # Configure main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box

        # Global keyboard shortcuts
        cmd_s = toga.Command(
            self.start_simulation,
            "Start Simulation",
            shortcut=toga.Key.MOD_1 + "s"
        )
        cmd_x = toga.Command(
            self.stop_simulation,
            "Stop Simulation",
            shortcut=toga.Key.MOD_1 + "x"
        )
        self.commands.add(cmd_s, cmd_x)
        self.main_window.show()

    def setup_components(self):
        self.action_simulator = ActionSimulator(self.text_box, self)
        self.key_handler = GlobalKeyHandler(self, self.action_simulator)
        self.simulation_task = None

    async def choose_file(self, widget):
        # Use the Toga dialog API for file selection
        dialog = toga.OpenFileDialog(
            title="Select a Code File",
            file_types=["txt"]
        )
        file_paths = await self.main_window.dialog(dialog)
        if file_paths:
            # Assuming single file selection
            self.selected_file = file_paths[0]
            # Only show the filename, not the entire path
            filename = os.path.basename(self.selected_file)
            self.file_display.text = f"Selected: {filename}"
            logger.info(f"Selected file: {self.selected_file}")
        else:
            self.selected_file = None
            self.file_display.text = "Using default resources/code files"
            logger.info("No file selected; using default.")

    async def start_simulation(self, widget):
        if not self.action_simulator.loop_flag:
            try:
                self.text_box.value = "🚀 Starting simulation...\n"
                self.update_button_states(running=True)
                self.action_simulator.loop_flag = True

                # Set simulation mode based on user selection
                selected_mode = self.mode_selector.value
                self.action_simulator.simulation_mode = selected_mode
                self.text_box.value += f"▶️ Mode: {selected_mode}\n"

                # If a file has been manually chosen and mode requires typing, pass that file.
                if self.selected_file and selected_mode in ["Typing Only", "Hybrid"]:
                    file_to_use = self.selected_file
                    filename = os.path.basename(file_to_use)
                    self.text_box.value += f"📄 Using selected file: {filename}\n"
                else:
                    file_to_use = None  # simulator will fall back to cycling default files
                    self.text_box.value += "📄 Using default code samples\n"

                if not self.simulation_task:
                    self.text_box.value += "⏳ Calculating typing time...\n"
                    self.simulation_task = asyncio.create_task(self.run_continuous_simulation(file_to_use))
                logger.info("Simulation started successfully.")
            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                await self.stop_simulation(widget)

    async def run_continuous_simulation(self, file_to_use: Optional[str]):
        try:
            while self.action_simulator.loop_flag:
                # If a file was manually chosen, use it; else, get the next available file.
                next_file = file_to_use if file_to_use else self.action_simulator.get_next_code_file()
                if not next_file:
                    self.text_box.value += "❌ No code files found in resources/code directory.\n"
                    await asyncio.sleep(2)
                    continue

                # Calculate estimated typing time
                if self.action_simulator.simulation_mode in ["Typing Only", "Hybrid"]:
                    await self.action_simulator.calculate_typing_time(next_file)

                # Run appropriate simulation based on mode
                if self.action_simulator.simulation_mode == "Typing Only":
                    self.text_box.value += "⌨️ Simulating typing...\n"
                    await self.action_simulator.simulate_typing(next_file)
                elif self.action_simulator.simulation_mode == "Tab Switching Only":
                    self.text_box.value += "🔄 Switching between applications...\n"
                    self.action_simulator.switch_window()
                    await asyncio.sleep(2)
                elif self.action_simulator.simulation_mode == "Hybrid":
                    self.text_box.value += "⌨️ Simulating typing...\n"
                    await self.action_simulator.simulate_typing(next_file)
                    self.text_box.value += "🔄 Switching between applications...\n"
                    self.action_simulator.switch_window()
                    await asyncio.sleep(2)

                filename = os.path.basename(next_file)
                self.text_box.value += f"\n✅ Finished simulating file: {filename}\n"
                self.text_box.value += "🔄 Cycle completed. Restarting...\n\n"
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            self.text_box.value += "⏹️ Simulation task cancelled.\n"
        except Exception as e:
            self.text_box.value += f"❌ Error during simulation: {str(e)}\n"
            logger.error(f"Error in continuous simulation: {e}")
            self.stop_simulation(None)

    async def stop_simulation(self, widget):
        if self.action_simulator.loop_flag:
            try:
                self.text_box.value += "⏹️ Stopping simulation...\n"
                self.action_simulator.loop_flag = False
                self.update_button_states(running=False)
                if self.simulation_task:
                    self.simulation_task.cancel()
                    self.simulation_task = None
                logger.info("Simulation stopped successfully.")
            except Exception as e:
                logger.error(f"Error stopping simulation: {e}")

    def update_button_states(self, running: bool):
        self.start_button.enabled = not running
        self.stop_button.enabled = running


def main():
    return CodeSimulator()
