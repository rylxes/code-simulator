import asyncio
import random
# import pyautogui # Deferred import
from typing import Optional, Tuple
from .logging_config import logger

pyautogui = None # Placeholder for the global


class MouseController:
    """Handles random mouse movements independently of typing simulation."""

    def __init__(self):
        """Initialize the mouse controller."""
        self.is_active = False
        self.pyautogui_initialized = False
        self.screen_width: Optional[int] = None
        self.screen_height: Optional[int] = None
        self.movement_task: Optional[asyncio.Task] = None
        self._init_pyautogui()

    def _init_pyautogui(self):
        global pyautogui
        try:
            import pyautogui as pgui
            pyautogui = pgui
            self.screen_width, self.screen_height = pyautogui.size()
            self.pyautogui_initialized = True
            logger.info("MouseController: PyAutoGUI initialized successfully.")
        except Exception as e:
            self.pyautogui_initialized = False
            logger.error(f"MouseController: PyAutoGUI failed to initialize: {e}", exc_info=True)
            # We don't show UI messages here; ActionSimulator handles primary PyAutoGUI error reporting.

    @property
    def is_running(self):
        return self.is_active and self.movement_task and not self.movement_task.done()

    async def start_random_movement(self,
                                    min_interval: float = 5.0,
                                    max_interval: float = 15.0,
                                    excluded_zone: Optional[Tuple[int, int, int, int]] = None):
        """
        Start random mouse movement in background.
        Args:
            min_interval: Minimum time between movements in seconds
            max_interval: Maximum time between movements in seconds
            excluded_zone: Tuple of (x1, y1, x2, y2) defining area to avoid
        """
        if not self.pyautogui_initialized or not pyautogui:
            logger.warning("MouseController: PyAutoGUI not available. Cannot start random movement.")
            self.is_active = False # Ensure it doesn't appear active
            return

        self.is_active = True
        logger.info("MouseController: Starting random mouse movement.")

        while self.is_active:
            try:
                # Generate random position
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)

                # Skip if in excluded zone
                if excluded_zone:
                    x1, y1, x2, y2 = excluded_zone
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        await asyncio.sleep(0.1) # Small pause if skipping
                        continue

                # Calculate smooth movement duration based on distance
                current_x, current_y = pyautogui.position()
                distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
                duration = min(1.0, max(0.1, distance / 2000)) # Adjusted duration calculation

                # Move mouse smoothly
                pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
                logger.debug(f"Moved mouse to ({x}, {y}) over {duration:.2f}s")

                # Random wait before next movement
                wait_time = random.uniform(min_interval, max_interval)
                await asyncio.sleep(wait_time)

            except pyautogui.FailSafeException:
                logger.warning("MouseController: PyAutoGUI FailSafeException triggered. Stopping mouse movement.")
                self.is_active = False # Stop on failsafe
            except Exception as e:
                if not self.is_active: # If stop was called, this exception might be due to task cancellation
                    logger.info("MouseController: Movement loop interrupted, possibly due to stop call.")
                    break
                logger.error(f"MouseController: Error in mouse movement: {e}", exc_info=True)
                await asyncio.sleep(max_interval) # Wait longer on error before retry
        logger.info("MouseController: Random mouse movement loop ended.")


    def start(self,
              min_interval: float = 5.0,
              max_interval: float = 15.0,
              excluded_zone: Optional[Tuple[int, int, int, int]] = None):
        """
        Start mouse movement in background task.
        Args:
            min_interval: Minimum time between movements
            max_interval: Maximum time between movements
            excluded_zone: Area to avoid (x1, y1, x2, y2)
        """
        if not self.pyautogui_initialized:
            logger.warning("MouseController: Cannot start, PyAutoGUI not initialized.")
            return

        if self.is_running:
            logger.debug("MouseController: Start called but already running.")
            return

        logger.info("MouseController: Initiating start of random movement task.")
        self.is_active = True # Set active before creating task
        self.movement_task = asyncio.create_task(
            self.start_random_movement(min_interval, max_interval, excluded_zone)
        )

    def stop(self):
        """Stop random mouse movement."""
        logger.info("MouseController: Stop requested.")
        self.is_active = False
        if self.movement_task and not self.movement_task.done():
            self.movement_task.cancel()
            logger.info("MouseController: Movement task cancellation requested.")
        self.movement_task = None # Clear the task reference