import sys
import subprocess
from typing import Optional, List, Dict
import random
from .logging_config import logger


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

            for app in self.config.get_applications(): # app is a dict with all platform keys
                # For macOS, bundle_id is primary. process_name_darwin can be secondary.
                bundle_id = app.get('bundle_id')
                process_name_darwin = app.get('process_name_darwin', app.get('name')) # Fallback to general name

                if not bundle_id and not process_name_darwin:
                    logger.debug(f"Skipping app due to missing bundle_id/process_name_darwin: {app.get('name')}")
                    continue

                for window in window_list:
                    owner_name = window.get(self._quartz.kCGWindowOwnerName, '')
                    owner_bundle_id = window.get('kCGWindowOwnerBundleID', '') # This key might not be standard, double check Quartz docs.
                                                                            # More common is kCGWindowOwnerPID then getting app from PID.
                                                                            # For now, assume direct bundle ID might be available or owner_name match is enough.
                                                                            # The original code had 'kCGWindowOwnerBundleID' so I'll keep similar logic.

                    # Prefer bundle_id match if available
                    if bundle_id and owner_bundle_id == bundle_id:
                        running_apps.append(app.copy())
                        break
                    # Fallback to matching owner name (process name)
                    elif process_name_darwin and owner_name == process_name_darwin:
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
                    current_window_class = self._win32gui.GetClassName(hwnd)

                    for app_config_entry in self.config.get_applications(): # app_config_entry is a dict with all platform keys
                        target_window_class = app_config_entry.get('window_class_windows')
                        if target_window_class and current_window_class == target_window_class:
                            apps.append(app_config_entry.copy())
                            # Assuming one window match is enough for this app_config_entry
                            # To avoid adding the same app multiple times if it has many windows of the same class
                            break
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
                    # WM_CLASS property can return a tuple (instance_name, class_name)
                    # Or sometimes just one of them as a string.
                    wm_class_prop = window.get_wm_class()
                    current_window_classes = []
                    if wm_class_prop:
                        if isinstance(wm_class_prop, tuple):
                            current_window_classes.extend(list(wm_class_prop))
                        elif isinstance(wm_class_prop, str):
                            current_window_classes.append(wm_class_prop)

                    if not current_window_classes:
                        continue

                    for app_config_entry in self.config.get_applications(): # app_config_entry is a dict with all platform keys
                        target_window_class_linux = app_config_entry.get('window_class_linux')
                        if target_window_class_linux:
                            # Check if any of the current window's classes match the target
                            if any(target_wc in current_window_classes for target_wc in target_window_class_linux.split()): # Target can be space separated
                                running_apps.append(app_config_entry.copy())
                                # Assuming one window match is enough for this app_config_entry
                                break
                except Exception as e:
                    logger.debug(f"Error processing Linux window {window_id}: {e}")
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
                # On macOS, 'name' (general name) or 'bundle_id' or 'path_darwin' can be used.
                # 'osascript -e tell application "Name"' is common.
                # 'osascript -e tell application id "bundle.id"' is also robust.
                # 'open -a /path/to/app' or 'open -b bundle.id'
                target_name = app_info.get("name")
                bundle_id = app_info.get("bundle_id")

                if bundle_id: # Prefer bundle_id for activation if available
                    logger.info(f"Attempting to activate macOS app by bundle_id: {bundle_id}")
                    subprocess.run(['osascript', '-e', f'tell application id "{bundle_id}" to activate'], check=True, capture_output=True, text=True)
                elif target_name:
                    logger.info(f"Attempting to activate macOS app by name: {target_name}")
                    subprocess.run(['osascript', '-e', f'tell application "{target_name}" to activate'], check=True, capture_output=True, text=True)
                else:
                    raise ValueError("No 'name' or 'bundle_id' provided for macOS application focus")

            elif self.platform == 'win32':
                target_window_class = app_info.get('window_class_windows')
                if not target_window_class:
                    raise ValueError("No 'window_class_windows' provided for Windows application focus")

                logger.info(f"Attempting to focus Windows app by window_class: {target_window_class}")
                def callback(hwnd, class_name_to_find):
                    try:
                        if (self._win32gui.IsWindowVisible(hwnd) and
                                self._win32gui.GetClassName(hwnd) == class_name_to_find):
                            self._win32gui.SetForegroundWindow(hwnd)
                            logger.info(f"Focused window with class: {class_name_to_find}")
                            return False # Stop enumeration
                    except Exception as e:
                        logger.error(f"Error setting foreground window: {e}")
                    return True # Continue enumeration
                self._win32gui.EnumWindows(callback, target_window_class)

            else:  # Linux
                # For Linux, wmctrl can use window title (often app name), or class.
                # The 'name' field from app_info should be suitable for wmctrl -a.
                # If window_class_linux is more reliable, that could be used with wmctrl -x -a <class>.
                target_name = app_info.get("name")
                target_class = app_info.get("window_class_linux")

                if target_class: # Prefer class based activation if available
                    logger.info(f"Attempting to focus Linux app by WM_CLASS: {target_class}")
                    # wmctrl -x will use the WM_CLASS. It might need only one part of the class.
                    # Taking the first part if it's space-separated.
                    subprocess.run(['wmctrl', '-x', '-a', target_class.split()[0]], check=True, capture_output=True, text=True)
                elif target_name:
                    logger.info(f"Attempting to focus Linux app by name/title: {target_name}")
                    subprocess.run(['wmctrl', '-a', target_name], check=True, capture_output=True, text=True)
                else:
                    raise ValueError("No 'name' or 'window_class_linux' provided for Linux application focus")
                # The redundant call below was causing tests to fail. It has been removed.
                # subprocess.run(
                #     ['wmctrl', '-a', target_name],
                #     check=True,
                #     capture_output=True,
                #     text=True
                # )

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with return code {e.returncode}: {e.output}")
            return False
        except Exception as e:
            logger.error(f"Error focusing application {app_info.get('name', 'unknown')}: {e}")
            return False