import asyncio
import sys
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from toga.colors import rgb
from .actions import ActionSimulator
from .key_handler import GlobalKeyHandler
from .logging_config import logger


class CodeSimulator(toga.App):
    def __init__(self):
        super().__init__(
            formal_name="Code Simulator",
            app_id="com.example.codesimulator"
        )
        # Store a manually selected file (if any)
        self.selected_file = None

    def startup(self):
        self.setup_ui()
        self.setup_components()
        logger.info("Application started successfully.")

    def setup_ui(self):
        # Header with title and subheader
        header = toga.Label(
            "Code Simulator",
            style=Pack(font_size=28, font_weight="bold", padding=(10, 0), text_align=CENTER)
        )
        subheader = toga.Label(
            "Select a simulation mode and optionally choose a code file. Then start the simulation.",
            style=Pack(font_size=14, color=rgb(80, 80, 80), padding=(0, 10), text_align=CENTER)
        )

        # Sidebar: simulation mode selector, file chooser and control buttons
        sidebar = toga.Box(style=Pack(direction=COLUMN, padding=10, background_color=rgb(250, 250, 250), width=250))
        mode_label = toga.Label(
            "Simulation Mode:",
            style=Pack(padding_bottom=5, font_size=12, font_weight="bold")
        )
        self.simulation_modes = ["Typing Only", "Tab Switching Only", "Hybrid"]
        self.mode_selector = toga.Selection(
            items=self.simulation_modes,
            value=self.simulation_modes[2],  # Default to Hybrid
            style=Pack(padding_bottom=20)
        )
        # File chooser area
        file_label = toga.Label(
            "Selected Code File:",
            style=Pack(padding_bottom=5, font_size=12, font_weight="bold")
        )
        self.file_display = toga.Label(
            "Using default resources/code files",
            style=Pack(padding_bottom=10, font_size=11, color=rgb(100, 100, 100))
        )
        choose_file_button = toga.Button(
            "Choose File",
            on_press=self.choose_file,
            style=Pack(padding=5, background_color=rgb(60, 180, 100), color="white")
        )
        self.start_button = toga.Button(
            "Start Simulation",
            on_press=self.start_simulation,
            style=Pack(padding=5, background_color=rgb(60, 120, 200), color="white")
        )
        self.stop_button = toga.Button(
            "Stop Simulation",
            on_press=self.stop_simulation,
            style=Pack(padding=5, background_color=rgb(200, 60, 60), color="white"),
            enabled=False
        )
        extra_settings_label = toga.Label(
            "Additional Settings (Coming Soon)",
            style=Pack(font_size=10, padding_top=20, color=rgb(120, 120, 120))
        )
        sidebar.add(mode_label)
        sidebar.add(self.mode_selector)
        sidebar.add(file_label)
        sidebar.add(self.file_display)
        sidebar.add(choose_file_button)
        sidebar.add(self.start_button)
        sidebar.add(self.stop_button)
        sidebar.add(extra_settings_label)

        # Main panel: scrollable text box for simulation log output.
        self.text_box = toga.MultilineTextInput(
            readonly=True,
            placeholder="Simulation log output will appear here...",
            style=Pack(flex=1, padding=10, font_family="monospace", background_color=rgb(250, 250, 250))
        )
        main_panel = toga.ScrollContainer(content=self.text_box, style=Pack(flex=1, padding=10))

        # Combine sidebar and main panel into a horizontal box
        content_box = toga.Box(style=Pack(direction=ROW, flex=1))
        content_box.add(sidebar)
        content_box.add(main_panel)

        # Overall layout: header on top, then content
        main_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        main_box.add(header)
        main_box.add(subheader)
        main_box.add(content_box)

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
        self.action_simulator = ActionSimulator(self.text_box)
        self.key_handler = GlobalKeyHandler(self, self.action_simulator)
        self.simulation_task = None

    async def choose_file(self, widget):
        # Use the new Toga dialog API for file selection
        dialog = toga.OpenFileDialog(
            title="Select a Code File",
            file_types=["*.txt"]
        )
        file_paths = await self.main_window.dialog(dialog)
        if file_paths:
            # Assuming single file selection
            self.selected_file = file_paths[0]
            self.file_display.text = self.selected_file
            logger.info(f"Selected file: {self.selected_file}")
        else:
            self.selected_file = None
            self.file_display.text = "Using default resources/code files"
            logger.info("No file selected; using default.")

    async def start_simulation(self, widget):
        if not self.action_simulator.loop_flag:
            try:
                self.text_box.value = "Starting simulation...\n"
                self.update_button_states(running=True)
                self.action_simulator.loop_flag = True

                # Set simulation mode based on user selection
                selected_mode = self.mode_selector.value
                self.action_simulator.simulation_mode = selected_mode

                # If a file has been manually chosen and mode requires typing, pass that file.
                if self.selected_file and selected_mode in ["Typing Only", "Hybrid"]:
                    file_to_use = self.selected_file
                else:
                    file_to_use = None  # simulator will fall back to cycling default files

                if not self.simulation_task:
                    self.simulation_task = asyncio.create_task(self.run_continuous_simulation(file_to_use))
                logger.info("Simulation started successfully.")
            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                await self.stop_simulation(widget)

    async def run_continuous_simulation(self, file_to_use: Optional[str]):
        while self.action_simulator.loop_flag:
            # If a file was manually chosen, use it; else, get the next available file.
            next_file = file_to_use if file_to_use else self.action_simulator.get_next_code_file()
            if not next_file:
                self.text_box.value += "No code files found in resources/code directory.\n"
                await asyncio.sleep(2)
                continue

            if self.action_simulator.simulation_mode == "Typing Only":
                await self.action_simulator.simulate_typing(next_file)
            elif self.action_simulator.simulation_mode == "Tab Switching Only":
                self.action_simulator.switch_window()
                await asyncio.sleep(2)
            elif self.action_simulator.simulation_mode == "Hybrid":
                await self.action_simulator.simulate_typing(next_file)
                self.action_simulator.switch_window()
                await asyncio.sleep(2)

            self.text_box.value += f"\nFinished simulating file: {next_file}\nCycle completed. Restarting...\n"
            await asyncio.sleep(2)

    async def stop_simulation(self, widget):
        if self.action_simulator.loop_flag:
            try:
                self.text_box.value += "Stopping simulation...\n"
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