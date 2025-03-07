import asyncio
import random
import pyautogui
from typing import Optional, Tuple
from .logging_config import logger


class MouseController:
    """Handles random mouse movements independently of typing simulation."""

    def __init__(self):
        """Initialize the mouse controller."""
        self.is_active = False
        self.screen_width, self.screen_height = pyautogui.size()
        self.movement_task: Optional[asyncio.Task] = None

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
        self.is_active = True

        while self.is_active:
            try:
                # Generate random position
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)

                # Skip if in excluded zone
                if excluded_zone:
                    x1, y1, x2, y2 = excluded_zone
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        continue

                # Calculate smooth movement duration based on distance
                current_x, current_y = pyautogui.position()
                distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
                duration = min(2.0, distance / 1000)  # Cap at 2 seconds

                # Move mouse smoothly
                pyautogui.moveTo(x, y, duration=duration)
                logger.debug(f"Moved mouse to ({x}, {y})")

                # Random wait before next movement
                wait_time = random.uniform(min_interval, max_interval)
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Error in mouse movement: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

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
        if self.movement_task and not self.movement_task.done():
            return

        self.movement_task = asyncio.create_task(
            self.start_random_movement(min_interval, max_interval, excluded_zone)
        )

    def stop(self):
        """Stop random mouse movement."""
        self.is_active = False
        if self.movement_task:
            self.movement_task.cancel()
            self.movement_task = None