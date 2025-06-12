import asyncio
from platform import system
import sys
from .logging_config import logger


class GlobalKeyHandler:

    def __init__(self, app, action_simulator):
        try:
            self.main_loop = asyncio.get_event_loop()
        except RuntimeError: # For example, if called from a thread where no loop is set
            logger.warning("Could not get current event loop in GlobalKeyHandler init. Using asyncio.new_event_loop().")
            # This might happen if Toga's main loop isn't the one asyncio.get_event_loop() sees by default
            # or if this class is initialized from a non-main thread without a loop.
            # A more robust solution might involve passing the Toga app's loop explicitly if available and suitable.
            # For now, this is a fallback. If Toga runs its own loop on the main thread,
            # get_event_loop() should ideally get that one if called from main thread.
            self.main_loop = asyncio.new_event_loop()
            # If new_event_loop is used, it might need to be run in a separate thread if this handler isn't on main.
            # However, Toga usually runs its main loop, and callbacks from foreign threads (pynput, Quartz)
            # need to schedule onto *that* specific loop.
            # Assuming Toga sets the main thread's loop for asyncio.get_event_loop() to find.
            # If app.loop is available and is an asyncio loop, that would be more direct:
            # self.main_loop = app.loop
            # For now, proceeding with get_event_loop() as primary.

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
                            logger.info("Global hotkey detected: Command+S (start/toggle simulation)")
                            asyncio.run_coroutine_threadsafe(self.toggle_simulation_async(), self.main_loop)
                            return None  # Consume event (important for macOS to prevent beeps/further processing)

                        # Check for Command+X (keycode 7)
                        if command_down and keycode == 7:  # 'X' key
                            logger.info("Global hotkey detected: Command+X (stop simulation)")
                            asyncio.run_coroutine_threadsafe(self.app.stop_simulation(None), self.main_loop)
                            return None  # Consume event
                except Exception as e:
                    logger.error(f"Error in macOS event handler: {e}", exc_info=True) # Added exc_info

                return event  # Let the event propagate

            # Specify the events we want to listen for (KeyDown and KeyUp can be useful for some stateful logic)
            # For simple hotkeys, KeyDown might be sufficient.
            mask = (Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown) |
                    Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)) # Using KeyDown and KeyUp as originally intended

            # Create the event tap using CGEventTapCreate
            self.event_tap = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,      # Tap into session events (all applications)
                Quartz.kCGHeadInsertEventTap,   # Insert at the head of the event tap list
                Quartz.kCGEventTapOptionDefault,# Default tap options (listen-only can be kCGEventTapOptionListenOnly)
                mask,                           # Mask for KeyDown and KeyUp events
                handle_event,                   # Callback function
                None                            # No user data (refcon)
            )

            if not self.event_tap:
                logger.error("Failed to create CGEventTap. Global hotkeys on macOS will likely not work. Please ensure the application has Accessibility permissions in System Settings > Privacy & Security.")
                self.loop_source = None # Ensure it's None
                return

            # Create a run loop source from the event tap
            self.loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
            if not self.loop_source:
                logger.error("Failed to create run loop source for CGEventTap.")
                # Attempt to clean up the event_tap if loop source creation fails
                if hasattr(self, 'event_tap') and self.event_tap: # Should exist if we got here
                    Quartz.CGEventTapEnable(self.event_tap, False) # Disable it
                    # Quartz.CFRelease(self.event_tap) # CFRelease is not directly available via PyObjC for CFMachPortRef
                self.event_tap = None
                return

            # Add the run loop source to the current run loop
            Quartz.CFRunLoopAddSource(
                Quartz.CFRunLoopGetCurrent(),
                self.loop_source,
                Quartz.kCFRunLoopDefaultMode
            )

            # Enable the event tap so it starts receiving events
            Quartz.CGEventTapEnable(self.event_tap, True)

            logger.info("macOS global key handler initialized successfully with CGEventTap.")
        except ImportError: # Keep specific ImportError for Quartz
            logger.error("Failed to import Quartz for macOS key handling. Global hotkeys will not be available.")
        except Exception as e:
            logger.error(f"Failed to initialize macOS key handler with CGEventTap: {e}", exc_info=True)
            if hasattr(self, 'event_tap') and self.event_tap: # Cleanup if partial setup failed
                 Quartz.CGEventTapEnable(self.event_tap, False)
                 self.event_tap = None
            if hasattr(self, 'loop_source') and self.loop_source : # Should not exist if event_tap failed first
                 self.loop_source = None


    def _setup_windows_handler(self):
        try:
            from pynput import keyboard

            def on_press(key):
                try:
                    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                        self.ctrl_pressed = True
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 's':
                        logger.info("Global hotkey detected: Ctrl+S (start/toggle simulation)")
                        asyncio.run_coroutine_threadsafe(self.toggle_simulation_async(), self.main_loop)
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        asyncio.run_coroutine_threadsafe(self.app.stop_simulation(None), self.main_loop)
                except AttributeError:
                    pass # pynput raises this for special keys if .char is accessed without check
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
                        logger.info("Global hotkey detected: Ctrl+S (start/toggle simulation)")
                        asyncio.run_coroutine_threadsafe(self.toggle_simulation_async(), self.main_loop)
                    elif hasattr(key, 'char') and self.ctrl_pressed and key.char and key.char.lower() == 'x':
                        logger.info("Global hotkey detected: Ctrl+X (stop simulation)")
                        asyncio.run_coroutine_threadsafe(self.app.stop_simulation(None), self.main_loop)
                except AttributeError:
                    pass # pynput raises this for special keys if .char is accessed without check
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

            if hasattr(self, 'event_tap') and self.event_tap and self.platform == 'darwin':
                import Quartz # Ensure Quartz is available for cleanup
                logger.info("Cleaning up macOS CGEventTap...")
                Quartz.CGEventTapEnable(self.event_tap, False)

                if hasattr(self, 'loop_source') and self.loop_source:
                    Quartz.CFRunLoopRemoveSource(
                        Quartz.CFRunLoopGetCurrent(),
                        self.loop_source,
                        Quartz.kCFRunLoopDefaultMode
                    )
                    logger.info("Removed run loop source.")
                    # self.loop_source = None # CFRelease not typically needed for CFRunLoopSourceRef with PyObjC

                # CFRelease is tricky with PyObjC for CFMachPortRef (event_tap).
                # Disabling and removing from run loop is usually sufficient and safer.
                # If direct release were needed and possible: Quartz.CFRelease(self.event_tap)
                self.event_tap = None
                self.loop_source = None # Ensure it's cleared
                logger.info("macOS CGEventTap cleanup completed.")

            logger.info("Key handler cleanup completed")
        except ImportError:
            logger.error("Failed to import Quartz during macOS cleanup. Some resources might not be released.")
        except Exception as e:
            logger.error(f"Error during key handler cleanup: {e}")