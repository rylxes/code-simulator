import sys
import logging
import subprocess
from typing import Optional, List, Dict
import random

logger = logging.getLogger(__name__)


class AppSwitcher:
    """
    Handles application switching across different platforms (macOS, Windows, Linux).
    Supports focusing applications and retrieving running application lists.
    """

    def __init__(self, config):
        """
        Initialize AppSwitcher with configuration.

        Args:
            config: Configuration object that provides application settings
        """
        self.config = config
        self.platform = sys.platform
        self._quartz = None
        self._win32gui = None
        self._win32process = None
        self._display = None
        self._setup_platform_handler()

    def _setup_platform_handler(self):
        """Set up the platform-specific handler based on the current operating system."""
        try:
            if self.platform == 'darwin':
                self._setup_macos_handler()
            elif self.platform == 'win32':
                self._setup_windows_handler()
            else:
                self._setup_linux_handler()
        except Exception as e:
            logger.error(f"Failed to setup platform handler: {e}")
            raise RuntimeError(f"Platform setup failed: {e}")

    def _setup_macos_handler(self):
        """Set up macOS specific handler by importing required modules."""
        try:
            import Quartz
            self._quartz = Quartz
        except ImportError as e:
            logger.error(f"Failed to import Quartz module for macOS: {e}")
            raise ImportError("Quartz module is required for macOS support")

    def _setup_windows_handler(self):
        """Set up Windows specific handler by importing required modules."""
        try:
            import win32gui
            import win32process
            self._win32gui = win32gui
            self._win32process = win32process
        except ImportError as e:
            logger.error(f"Failed to import win32gui/win32process modules: {e}")
            raise ImportError("win32gui and win32process modules are required for Windows support")

    def _setup_linux_handler(self):
        """Set up Linux specific handler by importing required modules."""
        try:
            import Xlib.display
            self._display = Xlib.display.Display()
        except ImportError as e:
            logger.error(f"Failed to import Xlib module: {e}")
            raise ImportError("Xlib module is required for Linux support")

    def _remove_duplicates(self, apps: List[Dict]) -> List[Dict]:
        """
        Remove duplicate applications based on their unique identifiers.

        Args:
            apps: List of application dictionaries

        Returns:
            List of unique application dictionaries
        """
        seen = set()
        unique_apps = []
        for app in apps:
            # Create a unique identifier from sorted items
            identifier = tuple(sorted((k, str(v)) for k, v in app.items()))
            if identifier not in seen:
                seen.add(identifier)
                unique_apps.append(app)
        return unique_apps

    def get_running_applications(self) -> List[Dict]:
        """
        Get list of configured applications that are currently running.

        Returns:
            List of running application configurations
        """
        if self.platform == 'darwin':
            return self._get_running_applications_macos()
        elif self.platform == 'win32':
            return self._get_running_applications_windows()
        else:
            return self._get_running_applications_linux()

    def _get_running_applications_macos(self) -> List[Dict]:
        """
        Get running applications on macOS.

        Returns:
            List of running application configurations
        """
        running_apps = []
        try:
            window_list = self._quartz.CGWindowListCopyWindowInfo(
                self._quartz.kCGWindowListOptionOnScreenOnly |
                self._quartz.kCGWindowListExcludeDesktopElements,
                self._quartz.kCGNullWindowID
            )

            if window_list:
                window_list = list(window_list)

            for app in self.config.get_applications():
                app_name = app.get('process_name', '')
                bundle_id = app.get('bundle_id', '')

                for window in window_list:
                    owner = window.get(self._quartz.kCGWindowOwnerName, '')
                    owner_bundle = window.get('kCGWindowOwnerBundleID', '')

                    if (owner and owner == app_name) or \
                            (bundle_id and owner_bundle == bundle_id):
                        running_apps.append(app.copy())
                        break

        except Exception as e:
            logger.error(f"Error getting macOS running applications: {e}")
            return []

        return self._remove_duplicates(running_apps)

    def _get_running_applications_windows(self) -> List[Dict]:
        """
        Get running applications on Windows.

        Returns:
            List of running application configurations
        """
        running_apps = []
        try:
            def callback(hwnd, apps):
                if not self._win32gui.IsWindowVisible(hwnd):
                    return True

                try:
                    _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
                    class_name = self._win32gui.GetClassName(hwnd)

                    for app in self.config.get_applications():
                        if class_name == app.get('window_class'):
                            apps.append(app.copy())
                except Exception as e:
                    logger.debug(f"Error processing window {hwnd}: {e}")
                return True

            self._win32gui.EnumWindows(callback, running_apps)
        except Exception as e:
            logger.error(f"Error getting Windows running applications: {e}")
            return []

        return self._remove_duplicates(running_apps)

    def _get_running_applications_linux(self) -> List[Dict]:
        """
        Get running applications on Linux.

        Returns:
            List of running application configurations
        """
        running_apps = []
        try:
            root = self._display.screen().root
            window_ids = root.get_full_property(
                self._display.intern_atom('_NET_CLIENT_LIST'),
                self._display.intern_atom('WINDOW')
            ).value

            for window_id in window_ids:
                window = self._display.create_resource_object('window', window_id)
                try:
                    window_class = window.get_wm_class()
                    if window_class:
                        for app in self.config.get_applications():
                            if app.get('window_class') in window_class:
                                running_apps.append(app.copy())
                except Exception as e:
                    logger.debug(f"Error processing window {window_id}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error getting Linux running applications: {e}")
            return []

        return self._remove_duplicates(running_apps)

    def get_random_running_app(self) -> Optional[Dict]:
        """
        Get a random running application from the configured list.

        Returns:
            Random application configuration or None if no applications are running
        """
        running_apps = self.get_running_applications()
        return random.choice(running_apps) if running_apps else None

    def focus_application(self, app_info: Dict) -> bool:
        """
        Focus on a specific application.

        Args:
            app_info: Dictionary containing application information

        Returns:
            bool: True if focus was successful, False otherwise
        """
        if not app_info:
            logger.error("Cannot focus: app_info is None or empty")
            return False

        try:
            if self.platform == 'darwin':
                app_name = app_info.get("name")
                if not app_name:
                    raise ValueError("No application name provided")
                subprocess.run(
                    ['osascript', '-e', f'tell application "{app_name}" to activate'],
                    check=True,
                    capture_output=True,
                    text=True
                )

            elif self.platform == 'win32':
                window_class = app_info.get('window_class')
                if not window_class:
                    raise ValueError("No window class provided")

                def callback(hwnd, class_name):
                    try:
                        if (self._win32gui.IsWindowVisible(hwnd) and
                                self._win32gui.GetClassName(hwnd) == class_name):
                            self._win32gui.SetForegroundWindow(hwnd)
                            return False
                    except Exception as e:
                        logger.error(f"Error setting foreground window: {e}")
                    return True

                self._win32gui.EnumWindows(callback, window_class)

            else:  # Linux
                app_name = app_info.get("name")
                if not app_name:
                    raise ValueError("No application name provided")
                subprocess.run(
                    ['wmctrl', '-a', app_name],
                    check=True,
                    capture_output=True,
                    text=True
                )

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with return code {e.returncode}: {e.output}")
            return False
        except Exception as e:
            logger.error(f"Error focusing application {app_info.get('name', 'unknown')}: {e}")
            return False