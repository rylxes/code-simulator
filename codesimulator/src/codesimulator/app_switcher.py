import sys
import logging
import subprocess
from typing import Optional
import random

logger = logging.getLogger(__name__)


class AppSwitcher:
    """Handles application switching across different platforms."""

    def __init__(self, config):
        self.config = config
        self.platform = sys.platform
        self._setup_platform_handler()

    def _setup_platform_handler(self):
        """Set up the platform-specific handler."""
        if self.platform == 'darwin':
            self._setup_macos_handler()
        elif self.platform == 'win32':
            self._setup_windows_handler()
        else:
            self._setup_linux_handler()

    def _setup_macos_handler(self):
        """Set up macOS specific handler."""
        try:
            # Import macOS specific modules
            import Quartz
            self._quartz = Quartz
        except ImportError:
            logger.error("Failed to import Quartz module for macOS")

    def _setup_windows_handler(self):
        """Set up Windows specific handler."""
        try:
            import win32gui
            import win32process
            self._win32gui = win32gui
            self._win32process = win32process
        except ImportError:
            logger.error("Failed to import win32gui/win32process modules")

    def _setup_linux_handler(self):
        """Set up Linux specific handler."""
        try:
            import Xlib.display
            self._display = Xlib.display.Display()
        except ImportError:
            logger.error("Failed to import Xlib module")

    def get_running_applications(self):
        """Get list of configured applications that are currently running."""
        if self.platform == 'darwin':
            return self._get_running_applications_macos()
        elif self.platform == 'win32':
            return self._get_running_applications_windows()
        else:
            return self._get_running_applications_linux()

    def _get_running_applications_macos(self):
        """Get running applications on macOS."""
        running_apps = []
        try:
            workspace = self._quartz.CGWorkspaceGetActiveSpace()
            apps = self._quartz.CGWindowListCopyWindowInfo(
                self._quartz.kCGWindowListOptionOnScreenOnly |
                self._quartz.kCGWindowListExcludeDesktopElements,
                0
            )

            for app in self.config.get_applications():
                bundle_id = app.get('bundle_id')
                if any(window.get(self._quartz.kCGWindowOwnerName) == app['process_name']
                       for window in apps):
                    running_apps.append(app)
        except Exception as e:
            logger.error(f"Error getting macOS running applications: {e}")

        return running_apps

    def _get_running_applications_windows(self):
        """Get running applications on Windows."""
        running_apps = []
        try:
            def callback(hwnd, apps):
                if self._win32gui.IsWindowVisible(hwnd):
                    _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
                    for app in self.config.get_applications():
                        try:
                            class_name = self._win32gui.GetClassName(hwnd)
                            if class_name == app.get('window_class'):
                                apps.append(app)
                        except Exception:
                            continue
                return True

            self._win32gui.EnumWindows(callback, running_apps)
        except Exception as e:
            logger.error(f"Error getting Windows running applications: {e}")

        return list(set(running_apps))

    def _get_running_applications_linux(self):
        """Get running applications on Linux."""
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
                                running_apps.append(app)
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error getting Linux running applications: {e}")

        return list(set(running_apps))

    def get_random_running_app(self) -> Optional[dict]:
        """Get a random running application from the configured list."""
        running_apps = self.get_running_applications()
        return random.choice(running_apps) if running_apps else None

    def focus_application(self, app_info: dict) -> bool:
        """Focus on a specific application."""
        try:
            if self.platform == 'darwin':
                subprocess.run(['osascript', '-e', f'tell application "{app_info["name"]}" to activate'])
            elif self.platform == 'win32':
                def callback(hwnd, app_info):
                    if self._win32gui.IsWindowVisible(hwnd):
                        class_name = self._win32gui.GetClassName(hwnd)
                        if class_name == app_info.get('window_class'):
                            self._win32gui.SetForegroundWindow(hwnd)
                            return False
                    return True

                self._win32gui.EnumWindows(callback, app_info)
            else:
                subprocess.run(['wmctrl', '-a', app_info['name']])
            return True
        except Exception as e:
            logger.error(f"Error focusing application: {e}")
            return False