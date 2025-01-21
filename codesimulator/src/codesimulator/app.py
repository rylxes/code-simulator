import asyncio
import sys

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from .actions import ActionSimulator
from .key_handler import GlobalKeyHandler
from .logging_config import logger



class CodeSimulator(toga.App):
    """Main application class for the code simulation."""

    def startup(self):
        """Initialize and show the Toga application."""
        self.setup_ui()
        self.setup_components()
        logger.info("Application started successfully.")

    def setup_ui(self):
        """Set up the user interface components."""
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # Create description label
        self.description_label = toga.Label(
            'Press keyboard shortcuts:\n'
            'Cmd/Ctrl + S to start simulation\n'
            'Cmd/Ctrl + X to stop simulation',
            style=Pack(padding=(0, 5))
        )

        # Create text output box
        self.text_box = toga.MultilineTextInput(
            readonly=True,
            placeholder="Press 'Start Simulation' to simulate writing code.",
            style=Pack(flex=1)
        )

        # Create control buttons
        self.start_button = toga.Button(
            "Start Simulation",
            on_press=self.start_simulation,
            style=Pack(padding=5)
        )

        self.stop_button = toga.Button(
            "Stop Simulation",
            on_press=self.stop_simulation,
            style=Pack(padding=5),
            enabled=False
        )

        # Add components to main box
        main_box.add(self.description_label)
        main_box.add(self.text_box)
        main_box.add(self.start_button)
        main_box.add(self.stop_button)

        # Create and show main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box

        # Create commands for keyboard shortcuts
        cmd_s = toga.Command(
            self.start_simulation,
            'Start Simulation',
            shortcut=toga.Key.MOD_1 + 's'
        )

        cmd_x = toga.Command(
            self.stop_simulation,
            'Stop Simulation',
            shortcut=toga.Key.MOD_1 + 'x'
        )

        self.commands.add(cmd_s, cmd_x)

        self.main_window.show()

    def setup_components(self):
        """Initialize application components."""
        self.action_simulator = ActionSimulator(self.text_box)
        self.key_handler = GlobalKeyHandler(self, self.action_simulator)
        self.simulation_task = None

    async def start_simulation(self, widget):
        """Start the simulation if not already running."""
        if not self.action_simulator.loop_flag:
            try:
                self.text_box.value = "Starting simulation...\n"
                self.update_button_states(running=True)
                self.action_simulator.loop_flag = True

                if not self.simulation_task:
                    self.simulation_task = asyncio.create_task(
                        self.action_simulator.simulate_typing()
                    )
                logger.info("Simulation started successfully.")
            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                await self.stop_simulation(widget)

    async def stop_simulation(self, widget):
        """Stop the running simulation."""
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
        """Update button states based on simulation status."""
        self.start_button.enabled = not running
        self.stop_button.enabled = running


def main():
    """Application entry point."""
    return CodeSimulator()