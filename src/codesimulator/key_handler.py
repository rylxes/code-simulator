import asyncio
from platform import system
import sys
from .logging_config import logger


class GlobalKeyHandler:

    def __init__(self, app, action_simulator):
        self.app = app
        self.action_simulator = action_simulator
        self.platform = sys.platform
        self.keyboard_listener = None
        self._listener_task = None
        self._setup_platform_handler()

    def _setup_platform_handler(self):
        try:
            if self.platform == 'darwin':
                self._setup_macos_handler()
            elif self.platform == 'win32':
                self._setup_windows_handler()
            else:
                self._setup_linux_handler()
        except Exception as e:
            logger.error(f"Error setting up key handler: {e}")

    def _setup_macos_handler(self):
        try:
            import Quartz
            from AppKit import NSEvent, NSKeyDownMask, NSSystemDefined, NSEventModifierFlagCommand

            # This is a better approach for macOS - it catches ALL events including when app not in focus
            def handle_event(proxy, event_type, event, refcon):
                try:
                    if event_type == Quartz.kCGEventKeyDown:
                        # Get the key code and modifier flags
                        keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
                        flags = Quartz.CGEventGetFlags(event)

                        # Command key is pressed
                        command_down = (flags & Quartz.kCGEventFlagMaskCommand) != 0

                        # Check for Command+S (keycode 1)
                        if command_down and keycode == 1:  # 'S' key
                            logger.info("Global hotkey detected: Command+S (start simulation)")
                            asyncio.create_task(self.toggle_simulation_async())
                            return None  # Let the event propagate

                        # Check for Command+X (keycode 7)
                        if command_down and keycode == 7:  # 'X' key
                            logger.info("Global hotkey detected: Command+X (stop simulation)")
                            asyncio.create_task(self.app.stop_simulation(None))
                            return None  # Let the event propagate
                except Exception as e:
                    logger.error(f"Error in macOS event handler: {e}")

                return event  # Let the event propagate

            # Create event tap
            self.event_tap = Quartz.CFMachPortCreateWithFix(
                None,
                handle_event,
                None,
                None
            )

            # Create a run loop source and add it to the current run loop
            loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
            Quartz.CFRunLoopAddSource(
                Quartz.CFRunLoopGetCurrent(),
                loop_source,
                Quartz.kCFRunLoopDefaultMode
            )

            # Enable the event tap
            Quartz.CGEventTapEnable(self.event_tap, True)

            # Specify the events we want to listen for
            mask = (Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
                    Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp))

            # Create the tap
            Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,  # Global events
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionDefault,
                mask,
                handle_event,
                None
            )

            logger.info("macOS global key handler initialized successfully with event tap")
        except ImportError as e:
            logger.error(f"Failed to import macOS modules: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize macOS key handler: {e}")

    def _setup_windows_handler(self):
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                        self.ctrl_pressed = True
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 's':
                        logger.info("Global hotkey detected: Ctrl+S (start simulation)")
                        # Use asyncio to handle the simulation toggle
                        asyncio.create_task(self.toggle_simulation_async())
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        # Use asyncio to handle stopping the simulation
                        asyncio.create_task(self.app.stop_simulation(None))
                except AttributeError:
                    pass
                except Exception as e:
                    logger.error(f"Error in keyboard handler: {e}")

            def on_release(key):
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_pressed = False

            self.ctrl_pressed = False

            # Create and start the keyboard listener as a non-blocking listener
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
                suppress=False  # Set to False to allow events to propagate
            )
            self.keyboard_listener.start()
            logger.info("Windows global key handler initialized successfully")
        except ImportError as e:
            logger.error(f"pynput module not found: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Windows key handler: {e}")

    def _setup_linux_handler(self):
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                        self.ctrl_pressed = True
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 's':
                        logger.info("Global hotkey detected: Ctrl+S (start simulation)")
                        # Use asyncio to handle the simulation toggle
                        asyncio.create_task(self.toggle_simulation_async())
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        # Use asyncio to handle stopping the simulation
                        asyncio.create_task(self.app.stop_simulation(None))
                except AttributeError:
                    pass
                except Exception as e:
                    logger.error(f"Error in keyboard handler: {e}")

            def on_release(key):
                if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                    self.ctrl_pressed = False

            self.ctrl_pressed = False

            # Create and start the keyboard listener as a non-blocking listener
            self.keyboard_listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release,
                suppress=False  # Set to False to allow events to propagate
            )
            self.keyboard_listener.start()
            logger.info("Linux global key handler initialized successfully")
        except ImportError as e:
            logger.error(f"pynput module not found: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Linux key handler: {e}")

    async def run(self):
        try:
            logger.info("Global key handler started")
            # This loop keeps the task alive
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Key handler task cancelled")
        except Exception as e:
            logger.error(f"Error in key handler: {e}")

    def start(self):
        """Start the global key handler if it's not already running"""
        if not self._listener_task or self._listener_task.done():
            self._listener_task = asyncio.create_task(self.run())
            logger.info("Started global key handler task")

    async def toggle_simulation_async(self):
        """Asynchronous version of toggle_simulation for use with asyncio"""
        try:
            if self.action_simulator.loop_flag:
                await self.app.stop_simulation(None)
            else:
                await self.app.start_simulation(None)
        except Exception as e:
            logger.error(f"Error in async toggle simulation: {e}")

    def toggle_simulation(self):
        """Synchronous version for backward compatibility"""
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

            if self._listener_task:
                self._listener_task.cancel()
                logger.info("Key handler task cancelled")

            if hasattr(self, 'event_tap') and self.platform == 'darwin':
                # Disable the event tap if we're on macOS
                import Quartz
                Quartz.CGEventTapEnable(self.event_tap, False)

            logger.info("Key handler cleanup completed")
        except Exception as e:
            logger.error(f"Error during key handler cleanup: {e}")