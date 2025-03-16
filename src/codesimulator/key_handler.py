import asyncio
from platform import system
import sys
from .logging_config import logger


class GlobalKeyHandler:

    def __init__(self, app, action_simulator):
        self.app = app
        self.action_simulator = action_simulator
        self.platform = sys.platform  # Using sys.platform for consistency with other files
        self.keyboard_listener = None
        self._setup_platform_handler()

    def _setup_platform_handler(self):
        try:
            if self.platform == 'darwin':
                self._setup_macos_handler()
            elif self.platform == 'win32':
                self._setup_windows_handler()
            else:  # linux and others
                self._setup_linux_handler()
        except Exception as e:
            logger.error(f"Error setting up key handler: {e}")

    def _setup_macos_handler(self):
        try:
            import Quartz
            from AppKit import NSEvent, NSKeyDownMask, NSEventModifierFlagCommand

            def handle_ns_event(event):
                if event.type() == NSKeyDownMask:
                    # Check if command key is pressed
                    command_key = (event.modifierFlags() & NSEventModifierFlagCommand) != 0
                    key = event.charactersIgnoringModifiers()

                    # Command+S to start/toggle simulation
                    if command_key and key.lower() == 's':
                        logger.info("Global hotkey detected: Command+S (start simulation)")
                        self.toggle_simulation()
                    # Command+X to stop simulation
                    elif command_key and key.lower() == 'x':
                        logger.info("Global hotkey detected: Command+X (stop simulation)")
                        self.app.stop_simulation(None)

            # Use the global monitor to capture events even when app is not in focus
            NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                NSKeyDownMask,
                handle_ns_event
            )
            logger.info("MacOS global key handler initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import MacOS modules: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize MacOS key handler: {e}")

    def _setup_windows_handler(self):
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    # Check for Ctrl+S to start/toggle simulation
                    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                        self.ctrl_pressed = True
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char.lower() == 's':
                        logger.info("Global hotkey detected: Ctrl+S (start simulation)")
                        self.toggle_simulation()
                    # Check for Ctrl+X to stop simulation
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        self.app.stop_simulation(None)
                except AttributeError:
                    # Special keys may not have a char attribute
                    pass
                except Exception as e:
                    logger.error(f"Error in keyboard handler: {e}")

            def on_release(key):
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_pressed = False

            # Initialize control key state
            self.ctrl_pressed = False

            # Create and start the listener
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.keyboard_listener.start()
            logger.info("Windows global key handler initialized successfully")
        except ImportError:
            logger.error("pynput module not found. Please install with: pip install pynput")
        except Exception as e:
            logger.error(f"Failed to initialize Windows key handler: {e}")

    def _setup_linux_handler(self):
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    # Check for Ctrl+S to start/toggle simulation
                    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                        self.ctrl_pressed = True
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 's':
                        logger.info("Global hotkey detected: Ctrl+S (start simulation)")
                        self.toggle_simulation()
                    # Check for Ctrl+X to stop simulation
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        self.app.stop_simulation(None)
                except AttributeError:
                    # Special keys may not have a char attribute
                    pass
                except Exception as e:
                    logger.error(f"Error in keyboard handler: {e}")

            def on_release(key):
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_pressed = False

            # Initialize control key state
            self.ctrl_pressed = False

            # Create and start the listener
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self.keyboard_listener.start()
            logger.info("Linux global key handler initialized successfully")
        except ImportError:
            logger.error("pynput module not found. Please install with: pip install pynput")
        except Exception as e:
            logger.error(f"Failed to initialize Linux key handler: {e}")

    async def run(self):
        try:
            logger.info("Global key handler started")
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("Key handler task cancelled")
        except Exception as e:
            logger.error(f"Error in key handler: {e}")

    def toggle_simulation(self):
        try:
            if self.action_simulator.loop_flag:
                self.app.stop_simulation(None)
            else:
                self.app.start_simulation(None)
        except Exception as e:
            logger.error(f"Error toggling simulation: {e}")

    def cleanup(self):
        try:
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                logger.info("Keyboard listener stopped")
            logger.info("Key handler cleanup completed")
        except Exception as e:
            logger.error(f"Error during key handler cleanup: {e}")