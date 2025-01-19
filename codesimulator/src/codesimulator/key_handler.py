import asyncio
import logging
import sys
from platform import system
from typing import Optional

logger = logging.getLogger(__name__)


class GlobalKeyHandler:
    """Handles global keyboard events across different platforms."""

    def __init__(self, app, action_simulator):
        """Initialize the key handler."""
        self.app = app
        self.action_simulator = action_simulator
        self.platform = system()
        self._setup_platform_handler()

    def _setup_platform_handler(self):
        """Set up the platform-specific key handler."""
        try:
            if self.platform == 'Darwin':
                self._setup_macos_handler()
            else:
                logger.info(f"Using default key handling for platform: {self.platform}")
        except Exception as e:
            logger.error(f"Error setting up key handler: {e}")

    def _setup_macos_handler(self):
        """Set up macOS-specific key handling using AppKit."""
        try:
            from AppKit import NSEvent, NSKeyDownMask

            def handle_ns_event(event):
                if event.type() == NSKeyDownMask:
                    key = event.charactersIgnoringModifiers()
                    if key in ["+", "="]:
                        self.toggle_simulation()
                    elif key == "-":
                        self.app.stop_simulation(None)

            NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                NSKeyDownMask,
                handle_ns_event
            )
            logger.info("MacOS key handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MacOS key handler: {e}")

    async def run(self):
        """Run the key handler background task."""
        try:
            logger.info("Global key handler started")
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("Key handler task cancelled")
        except Exception as e:
            logger.error(f"Error in key handler: {e}")

    def toggle_simulation(self):
        """Toggle the simulation state."""
        try:
            if self.action_simulator.loop_flag:
                self.app.stop_simulation(None)
            else:
                self.app.start_simulation(None)
        except Exception as e:
            logger.error(f"Error toggling simulation: {e}")

    def cleanup(self):
        """Clean up resources and handlers."""
        try:
            if self.platform == 'Darwin':
                # Add cleanup for MacOS specific resources if needed
                pass
            logger.info("Key handler cleanup completed")
        except Exception as e:
            logger.error(f"Error during key handler cleanup: {e}")