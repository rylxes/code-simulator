import asyncio
import os
import json
import tempfile
import platform
import random
import subprocess
import sys
from typing import Optional
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, LEFT, RIGHT
from toga.colors import rgb, rgba
from .actions import ActionSimulator
from .key_handler import GlobalKeyHandler
from .logging_config import get_log_path, setup_file_logging, logger
from .path_utils import log_environment_info, get_log_path

log_environment_info()


class CodeSimulator(toga.App):
    def __init__(self):
        super().__init__(
            formal_name="Code Simulator",
            app_id="com.example.codesimulator"
        )

        self.selected_file = None
        self.current_view = "simulation"  # Default view

    async def show_debug_info(self, widget):
        info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Python Version": platform.python_version(),
            "App Directory": os.path.dirname(os.path.abspath(__file__)),
            "Current Directory": os.getcwd(),
            "Log File": get_log_path(),
            "Is Packaged": getattr(sys, 'frozen', False),
            "Executable": sys.executable
        }

        self.console.value = "--- Debug Information ---\n\n"
        for key, value in info.items():
            self.console.value += f"{key}: {value}\n"

        log_environment_info()
        self.console.value += "\nDetailed debug information has been logged to the log file.\n"

    async def view_console_logs(self, widget):
        try:
            if platform.system() == "Darwin":
                process = subprocess.Popen(
                    ["log", "show", "--predicate", "process == 'Code Simulator'", "--last", "1h"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate(timeout=5)

                if stdout:
                    self.console.value = "Recent Console Logs:\n\n" + stdout
                else:
                    self.console.value = "No recent console logs found.\n"
                    if stderr:
                        self.console.value += f"Error: {stderr}\n"
            else:
                self.console.value = "Console log viewing only supported on macOS."
        except Exception as e:
            self.console.value = f"Error viewing console logs: {e}"

    async def view_logs(self, widget):
        setup_file_logging()
        log_path = get_log_path()

        self.console.value = "Log Information\n"
        self.console.value += "=============\n\n"
        self.console.value += f"Log file location: {log_path}\n\n"

        logger.info("Test log message from View Logs button")

        if not os.path.exists(log_path):
            self.console.value += f"❌ Log file still not found after write attempt!\n\n"

            try:
                log_dir = os.path.dirname(log_path)
                test_file_path = os.path.join(log_dir, "test_write.txt")
                with open(test_file_path, 'w') as f:
                    f.write("Test write")
                self.console.value += f"✓ Successfully created test file at: {test_file_path}\n"
                os.remove(test_file_path)
            except Exception as e:
                self.console.value += f"❌ Could not write test file: {e}\n"
                self.console.value += "This suggests a permissions issue or the directory doesn't exist\n"

            self.console.value += "\nEnvironment Information:\n"
            self.console.value += f"Working directory: {os.getcwd()}\n"
            self.console.value += f"Home directory: {os.path.expanduser('~')}\n"
            self.console.value += f"App directory: {os.path.dirname(__file__)}\n"
            self.console.value += f"Python executable: {sys.executable}\n"
            self.console.value += f"Is packaged: {getattr(sys, 'frozen', False)}\n"

            self.console.value += "\nTry looking for logs in these locations:\n"
            self.console.value += f"1. {os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')}\n"
            self.console.value += f"2. {tempfile.gettempdir()}\n"

            return

        file_size = os.path.getsize(log_path)
        last_modified = os.path.getmtime(log_path)
        import datetime
        mod_time = datetime.datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')

        self.console.value += f"Log file size: {file_size} bytes\n"
        self.console.value += f"Last modified: {mod_time}\n\n"

        try:
            with open(log_path, 'r') as f:
                if file_size > 10000:
                    self.console.value += f"Log file is large. Showing last portion...\n\n"
                    f.seek(max(0, file_size - 10000))
                    f.readline()
                    content = f.read()
                else:
                    content = f.read()

            self.console.value += "Log Content:\n"
            self.console.value += "===========\n\n"
            self.console.value += content

        except Exception as e:
            self.console.value += f"❌ Error reading log file: {e}\n"

    def startup(self):
        from .logging_config import setup_file_logging
        setup_file_logging()

        self.setup_ui()
        self.setup_components()
        logger.info("Application started successfully.")

    def setup_colors(self):
        """Set up the color theme for the application."""
        self.colors = {
            'primary': rgb(41, 98, 255),  # Main brand color
            'secondary': rgb(0, 163, 92),  # Secondary brand color
            'accent': rgb(83, 186, 122),  # Accent color for highlights
            'danger': rgb(235, 64, 52),  # Danger/warning color
            'background': rgb(245, 247, 250),  # Main background color
            'card': rgb(255, 255, 255),  # Card background color
            'text': rgb(33, 33, 33),  # Main text color
            'text_light': rgb(108, 117, 125),  # Secondary text color
            'border': rgb(222, 226, 230),  # Border color
            'menu_bg': rgb(32, 41, 64),  # Side menu background
            'menu_text': rgb(255, 255, 255),  # Side menu text
            'menu_selected': rgb(53, 63, 88),  # Selected menu item
            'menu_hover': rgb(47, 56, 80),  # Hover state for menu
            'status_success': rgb(25, 135, 84),  # Success status color
            'status_warning': rgb(255, 193, 7),  # Warning status color
            'status_error': rgb(220, 53, 69),  # Error status color
            'toolbar': rgb(52, 58, 64),  # Toolbar background
            'toolbar_text': rgb(255, 255, 255),  # Toolbar text
        }

    def setup_ui(self):
        """Create the main UI layout."""
        self.setup_colors()

        # Main container
        main_box = toga.Box(style=Pack(direction=ROW, flex=1))

        # 1. Create the side menu
        self.side_menu = self.create_side_menu()
        # Set a fixed width for the side menu
        self.side_menu.style.width = 220
        main_box.add(self.side_menu)

        # 2. Create the content area container that will change based on selected view
        self.content_container = toga.Box(style=Pack(
            direction=COLUMN,
            flex=1,
            background_color=self.colors['background']
        ))
        main_box.add(self.content_container)

        # 3. Build all possible views
        self.simulation_view = self.create_simulation_view()
        self.configuration_view = self.create_configuration_view()
        self.logs_view = self.create_logs_view()
        self.about_view = self.create_about_view()

        # 4. Set the initial view
        self.show_view("simulation")

        # 5. Set up the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box

        # 6. Set up keyboard shortcuts
        cmd_s = toga.Command(
            self.start_simulation,
            "Start Simulation",
            shortcut=toga.Key.MOD_1 + "s"
        )
        cmd_x = toga.Command(
            self.stop_simulation,
            "Stop Simulation",
            shortcut=toga.Key.MOD_1 + "x"
        )
        self.commands.add(cmd_s, cmd_x)

        # 7. Display the window
        self.main_window.show()

    def create_side_menu(self):
        """Create the side menu with navigation options."""
        side_menu = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['menu_bg'],
            padding=(0, 0),
            flex=1
        ))

        # App title/logo header
        logo_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(20, 15),
            alignment=CENTER
        ))

        title = toga.Label(
            "Code Simulator",
            style=Pack(
                font_size=18,
                font_weight="bold",
                color=self.colors['menu_text'],
                text_align=CENTER
            )
        )

        subtitle = toga.Label(
            "v0.0.1",
            style=Pack(
                font_size=12,
                color=rgba(255, 255, 255, 0.7),
                text_align=CENTER,
                padding_top=5
            )
        )

        logo_box.add(title)
        logo_box.add(subtitle)
        side_menu.add(logo_box)

        # Menu item divider
        divider = toga.Divider(style=Pack(
            padding=(0, 15),
        ))
        divider.style.color = rgba(255, 255, 255, 0.2)
        side_menu.add(divider)

        # Menu items
        self.menu_items = {}
        menu_options = [
            ("simulation", "Simulation", "⌨️"),
            ("configuration", "Configuration", "⚙️"),
            ("logs", "Logs & Debug", "📊"),
            ("about", "About & Help", "ℹ️")
        ]

        # Create menu items
        for item_id, label, icon in menu_options:
            menu_item = self.create_menu_item(item_id, label, icon)
            side_menu.add(menu_item)
            self.menu_items[item_id] = menu_item

        # Add a stretching box to push status to the bottom
        side_menu.add(toga.Box(style=Pack(flex=1)))

        # Status box at the bottom
        status_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(15, 15),
        ))
        # Set the background color after creation
        status_box.style.background_color = rgba(0, 0, 0, 0.2)

        status_label = toga.Label(
            "Ready",
            style=Pack(
                font_size=12,
                color=self.colors['menu_text'],
                padding=(5, 5)
            )
        )
        self.status_label = status_label
        status_box.add(status_label)

        side_menu.add(status_box)

        return side_menu

    def create_menu_item(self, item_id, label, icon):
        """Create a menu item button with icon and label."""
        # Create the menu item box
        menu_item = toga.Box(style=Pack(
            direction=ROW,
            padding=(12, 15),
            alignment=CENTER,
        ))

        # Icon
        icon_label = toga.Label(
            icon,
            style=Pack(
                font_size=16,
                color=self.colors['menu_text'],
                width=25,
                text_align=CENTER
            )
        )

        # Label
        text_label = toga.Label(
            label,
            style=Pack(
                font_size=14,
                color=self.colors['menu_text'],
                padding_left=10,
                text_align=LEFT,
                flex=1
            )
        )

        menu_item.add(icon_label)
        menu_item.add(text_label)

        # Create button with minimal styling
        button = toga.Button(
            "",
            on_press=lambda widget: self.show_view(item_id),
            style=Pack(
                padding=0,
                flex=1
            )
        )
        # Make the button transparent
        button.style.background_color = rgba(0, 0, 0, 0)

        menu_item.add(button)

        # Set menu item as selected if it's the current view
        if item_id == self.current_view:
            menu_item.style.background_color = self.colors['menu_selected']

        return menu_item

    def show_view(self, view_name):
        """Switch to the specified view."""
        # First, clear the content container
        for child in self.content_container.children:
            self.content_container.remove(child)

        # Update menu selection styling
        for item_id, menu_item in self.menu_items.items():
            if item_id == view_name:
                # Set the background color for the selected item
                menu_item.style.background_color = self.colors['menu_selected']
            else:
                # For non-selected items, reset to menu background color
                menu_item.style.background_color = self.colors['menu_bg']

        # Set the current view and add the appropriate content
        self.current_view = view_name

        if view_name == "simulation":
            self.content_container.add(self.simulation_view)
        elif view_name == "configuration":
            self.content_container.add(self.configuration_view)
        elif view_name == "logs":
            self.content_container.add(self.logs_view)
        elif view_name == "about":
            self.content_container.add(self.about_view)

    def create_simulation_view(self):
        """Create the main simulation view."""
        simulation_view = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['background'],
            padding=(20, 20),
            flex=1
        ))

        # Top toolbar section
        toolbar = toga.Box(style=Pack(
            direction=ROW,
            padding=(15, 10),
            background_color=self.colors['primary'],
            alignment=CENTER
        ))

        # Toolbar title
        toolbar_title = toga.Label(
            "Simulation Control",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['toolbar_text'],
                flex=1
            )
        )
        toolbar.add(toolbar_title)

        # Toolbar buttons
        self.start_button = toga.Button(
            "Start Simulation",
            on_press=self.start_simulation,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['secondary'],
                color=self.colors['toolbar_text'],
                font_weight="bold"
            )
        )

        self.stop_button = toga.Button(
            "Stop",
            on_press=self.stop_simulation,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['danger'],
                color=self.colors['toolbar_text'],
                font_weight="bold"
            ),
            enabled=False
        )

        toolbar.add(self.start_button)
        toolbar.add(toga.Box(style=Pack(width=10)))  # Spacer
        toolbar.add(self.stop_button)

        simulation_view.add(toolbar)

        # Main content with card design
        content_card = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['card'],
            padding=(20, 20),
            flex=1,
            
            
        ))

        # Simulation settings section
        settings_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 10, 0)
        ))

        settings_title = toga.Label(
            "Simulation Settings",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        settings_box.add(settings_title)

        # Mode selection
        mode_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 15, 0),
            alignment=CENTER
        ))

        mode_label = toga.Label(
            "Mode:",
            style=Pack(
                width=100,
                color=self.colors['text']
            )
        )

        self.simulation_modes = [
            "Typing Only",
            "Tab Switching Only",
            "Hybrid",
            "Mouse and Command+Tab"
        ]

        self.mode_selector = toga.Selection(
            items=self.simulation_modes,
            value=self.simulation_modes[2],
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        mode_box.add(mode_label)
        mode_box.add(self.mode_selector)
        settings_box.add(mode_box)

        # File selection
        file_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 15, 0),
            alignment=CENTER
        ))

        file_label = toga.Label(
            "File:",
            style=Pack(
                width=100,
                color=self.colors['text']
            )
        )

        self.file_display = toga.Label(
            "Using default resources/code files",
            style=Pack(
                flex=1,
                color=self.colors['text_light'],
                padding=(5, 5)
            )
        )

        choose_file_button = toga.Button(
            "Choose File",
            on_press=self.choose_file,
            style=Pack(
                padding=(5, 10),
                background_color=self.colors['accent'],
                color=self.colors['toolbar_text']
            )
        )

        file_box.add(file_label)
        file_box.add(self.file_display)
        file_box.add(toga.Box(style=Pack(width=10)))  # Spacer
        file_box.add(choose_file_button)
        settings_box.add(file_box)

        content_card.add(settings_box)

        # Divider
        content_card.add(toga.Divider(style=Pack(
            padding=(10, 0)
        )))

        # Console output section
        console_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(10, 0, 0, 0),
            flex=1
        ))

        console_title = toga.Label(
            "Simulation Log",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        console_box.add(console_title)

        self.console = toga.MultilineTextInput(
            readonly=True,
            style=Pack(
                flex=1,
                background_color=rgb(250, 250, 250)
            )
        )
        console_box.add(self.console)

        content_card.add(console_box)
        simulation_view.add(content_card)

        # Status footer
        status_bar = toga.Box(style=Pack(
            direction=ROW,
            padding=(10, 10),
            background_color=self.colors['card'],
            
            
        ))

        keyboard_shortcut_label = toga.Label(
            "Keyboard Shortcuts: ⌘+S = Start Simulation | ⌘+X = Stop Simulation",
            style=Pack(
                font_size=12,
                color=self.colors['text_light']
            )
        )
        status_bar.add(keyboard_shortcut_label)

        simulation_view.add(status_bar)

        return simulation_view

    def create_configuration_view(self):
        """Create the configuration view."""
        configuration_view = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['background'],
            padding=(20, 20),
            flex=1
        ))

        # Top toolbar
        toolbar = toga.Box(style=Pack(
            direction=ROW,
            padding=(15, 10),
            background_color=self.colors['primary'],
            alignment=CENTER
        ))

        toolbar_title = toga.Label(
            "Configuration",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['toolbar_text'],
                flex=1
            )
        )
        toolbar.add(toolbar_title)

        # Save configuration button
        save_config_button = toga.Button(
            "Save Settings",
            on_press=self.save_configuration_direct,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['secondary'],
                color=self.colors['toolbar_text'],
                font_weight="bold"
            )
        )
        toolbar.add(save_config_button)

        configuration_view.add(toolbar)

        # Main content with card design
        content_card = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['card'],
            padding=(20, 20),
            flex=1,
            
            
        ))

        # Create a scroll container to hold all settings
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        settings_box = toga.Box(style=Pack(direction=COLUMN, padding=(0, 10)))

        # Code Configuration Section
        code_section = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 20, 0)
        ))

        code_title = toga.Label(
            "Code Configuration",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        code_section.add(code_title)

        # Language selection
        language_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        language_label = toga.Label(
            "Language:",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.language_input = toga.Selection(
            items=["python", "java", "php"],
            value="python",
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        language_box.add(language_label)
        language_box.add(self.language_input)
        code_section.add(language_box)

        # Indent size
        indent_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        indent_label = toga.Label(
            "Indent Size:",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.indent_input = toga.NumberInput(
            min_value=1,
            max_value=8,
            step=1,
            value=4,
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        indent_box.add(indent_label)
        indent_box.add(self.indent_input)
        code_section.add(indent_box)

        # Max line length
        max_line_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        max_line_label = toga.Label(
            "Max Line Length:",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.max_line_input = toga.NumberInput(
            min_value=40,
            max_value=120,
            step=1,
            value=80,
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        max_line_box.add(max_line_label)
        max_line_box.add(self.max_line_input)
        code_section.add(max_line_box)

        settings_box.add(code_section)

        # Divider
        settings_box.add(toga.Divider(style=Pack(
            padding=(0, 10)
        )))

        # Typing Speed Configuration Section
        typing_section = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 20, 0)
        ))

        typing_title = toga.Label(
            "Typing Speed Configuration",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        typing_section.add(typing_title)

        # Min typing speed
        min_speed_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        min_speed_label = toga.Label(
            "Min Speed (sec):",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.min_speed_input = toga.NumberInput(
            min_value=0.01,
            max_value=0.5,
            step=0.01,
            value=0.15,
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        min_speed_box.add(min_speed_label)
        min_speed_box.add(self.min_speed_input)
        typing_section.add(min_speed_box)

        # Max typing speed
        max_speed_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        max_speed_label = toga.Label(
            "Max Speed (sec):",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.max_speed_input = toga.NumberInput(
            min_value=0.01,
            max_value=0.5,
            step=0.01,
            value=0.25,
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        max_speed_box.add(max_speed_label)
        max_speed_box.add(self.max_speed_input)
        typing_section.add(max_speed_box)

        # Mistake rate
        mistake_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 10, 0),
            alignment=CENTER
        ))

        mistake_label = toga.Label(
            "Mistake Rate:",
            style=Pack(
                width=150,
                color=self.colors['text']
            )
        )

        self.mistake_input = toga.NumberInput(
            min_value=0,
            max_value=0.5,
            step=0.01,
            value=0.09,
            style=Pack(
                flex=1,
                padding=(5, 5)
            )
        )

        mistake_box.add(mistake_label)
        mistake_box.add(self.mistake_input)
        typing_section.add(mistake_box)

        settings_box.add(typing_section)

        # Divider
        settings_box.add(toga.Divider(style=Pack(
            padding=(0, 10)
        )))

        # Applications Configuration Section
        apps_section = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 20, 0)
        ))

        apps_title = toga.Label(
            "Applications Configuration",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        apps_section.add(apps_title)

        # Applications list (placeholder)
        apps_info = toga.Label(
            "Application settings are configured in applications.json.\nThe simulator will switch between these applications during simulation.",
            style=Pack(
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        apps_section.add(apps_info)

        settings_box.add(apps_section)

        # Add the settings box to the scroll container
        scroll_container.content = settings_box
        content_card.add(scroll_container)

        # Add content card to the view
        configuration_view.add(content_card)

        # Load the initial configuration values
        # Note: We'll load values in setup_components after ActionSimulator is initialized

        return configuration_view

    def create_logs_view(self):
        """Create the logs and debugging view."""
        logs_view = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['background'],
            padding=(20, 20),
            flex=1
        ))

        # Top toolbar
        toolbar = toga.Box(style=Pack(
            direction=ROW,
            padding=(15, 10),
            background_color=self.colors['primary'],
            alignment=CENTER
        ))

        toolbar_title = toga.Label(
            "Logs & Debugging",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['toolbar_text'],
                flex=1
            )
        )
        toolbar.add(toolbar_title)

        logs_view.add(toolbar)

        # Main content with card design
        content_card = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['card'],
            padding=(20, 20),
            flex=1,
            
            
        ))

        # Debug buttons
        buttons_box = toga.Box(style=Pack(
            direction=ROW,
            padding=(0, 0, 15, 0)
        ))

        view_logs_button = toga.Button(
            "View Application Logs",
            on_press=self.view_logs,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['primary'],
                color=self.colors['toolbar_text'],
            )
        )

        debug_info_button = toga.Button(
            "Show Debug Info",
            on_press=self.show_debug_info,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['primary'],
                color=self.colors['toolbar_text'],
            )
        )

        console_logs_button = toga.Button(
            "View Console Logs",
            on_press=self.view_console_logs,
            style=Pack(
                padding=(10, 15),
                background_color=self.colors['primary'],
                color=self.colors['toolbar_text']
            )
        )

        buttons_box.add(view_logs_button)
        buttons_box.add(debug_info_button)
        buttons_box.add(console_logs_button)
        content_card.add(buttons_box)

        # Divider
        content_card.add(toga.Divider(style=Pack(
            padding=(10, 0)
        )))

        # Log output section
        log_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(10, 0, 0, 0),
            flex=1
        ))

        log_title = toga.Label(
            "Log Output",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        log_box.add(log_title)

        log_instructions = toga.Label(
            "Click one of the buttons above to view logs or debug information.",
            style=Pack(
                color=self.colors['text_light'],
                padding_bottom=10
            )
        )
        log_box.add(log_instructions)

        # This uses the same console widget as the simulation view
        # since we don't need two separate consoles
        log_console = toga.MultilineTextInput(
            readonly=True,
            style=Pack(
                flex=1,
                background_color=rgb(250, 250, 250)
            )
        )
        # Share the console between views
        self.console = log_console
        log_box.add(log_console)

        content_card.add(log_box)
        logs_view.add(content_card)

        return logs_view

    def create_about_view(self):
        """Create the about and help view."""
        about_view = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['background'],
            padding=(20, 20),
            flex=1
        ))

        # Top toolbar
        toolbar = toga.Box(style=Pack(
            direction=ROW,
            padding=(15, 10),
            background_color=self.colors['primary'],
            alignment=CENTER
        ))

        toolbar_title = toga.Label(
            "About & Help",
            style=Pack(
                font_size=16,
                font_weight="bold",
                color=self.colors['toolbar_text'],
                flex=1
            )
        )
        toolbar.add(toolbar_title)

        about_view.add(toolbar)

        # Main content with card design
        content_card = toga.Box(style=Pack(
            direction=COLUMN,
            background_color=self.colors['card'],
            padding=(20, 20),
            flex=1,
            
            
        ))

        # Create a scroll container for about content
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        about_content = toga.Box(style=Pack(direction=COLUMN, padding=(0, 0)))

        # App information section
        app_info_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(0, 0, 20, 0)
        ))

        app_name = toga.Label(
            "Code Simulator",
            style=Pack(
                font_size=24,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=5
            )
        )
        app_info_box.add(app_name)

        app_version = toga.Label(
            "Version 0.0.1",
            style=Pack(
                font_size=14,
                color=self.colors['text_light'],
                padding_bottom=10
            )
        )
        app_info_box.add(app_version)

        app_description = toga.Label(
            "Code Simulator is a tool for simulating coding activity including typing, window switching, and mouse movements. It's designed to create a realistic coding environment simulation.",
            style=Pack(
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        app_info_box.add(app_description)

        copyright_label = toga.Label(
            "© 2025 rylxes. All rights reserved.",
            style=Pack(
                font_size=12,
                color=self.colors['text_light'],
                padding_bottom=20
            )
        )
        app_info_box.add(copyright_label)

        about_content.add(app_info_box)

        # Divider
        about_content.add(toga.Divider(style=Pack(
            padding=(0, 10)
        )))

        # Help section
        help_box = toga.Box(style=Pack(
            direction=COLUMN,
            padding=(10, 0, 20, 0)
        ))

        help_title = toga.Label(
            "How to Use",
            style=Pack(
                font_size=18,
                font_weight="bold",
                color=self.colors['text'],
                padding_bottom=10
            )
        )
        help_box.add(help_title)

        # Help content
        help_sections = [
            ("Simulation Modes", [
                "Typing Only: Simulates keyboard typing from a code file",
                "Tab Switching Only: Simulates switching between application windows",
                "Hybrid: Combines typing and application switching",
                "Mouse and Command+Tab: Simulates mouse movements and Command+Tab switching"
            ]),
            ("File Selection", [
                "Use the 'Choose File' button to select a .txt file for typing simulation",
                "If no file is selected, default files from resources/code directory will be used"
            ]),
            ("Configuration", [
                "Adjust typing speed, language formatting, and other settings in the Configuration tab",
                "Application targets for switching can be configured in applications.json"
            ]),
            ("Keyboard Shortcuts", [
                "⌘+S: Start Simulation",
                "⌘+X: Stop Simulation"
            ])
        ]

        for section_title, items in help_sections:
            section_label = toga.Label(
                section_title,
                style=Pack(
                    font_size=16,
                    font_weight="bold",
                    color=self.colors['text'],
                    padding=(10, 0, 5, 0)
                )
            )
            help_box.add(section_label)

            for item in items:
                item_label = toga.Label(
                    "• " + item,
                    style=Pack(
                        color=self.colors['text'],
                        padding=(0, 0, 5, 15)
                    )
                )
                help_box.add(item_label)

        about_content.add(help_box)

        # Add the about content to the scroll container
        scroll_container.content = about_content
        content_card.add(scroll_container)

        # Add content card to the view
        about_view.add(content_card)

        return about_view

    def load_configuration_values(self):
        """Load configuration values from config.json."""
        try:
            # Get configuration path
            config_path = self.action_simulator._get_config_path()

            # Read configuration file
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Set code configuration values
            code_config = config.get('code', {})
            self.language_input.value = code_config.get('language', 'python')
            self.indent_input.value = code_config.get('indent_size', 4)
            self.max_line_input.value = code_config.get('max_line_length', 80)

            # Set typing speed configuration values
            typing_config = config.get('typing_speed', {})
            self.min_speed_input.value = typing_config.get('min', 0.03)
            self.max_speed_input.value = typing_config.get('max', 0.07)
            self.mistake_input.value = typing_config.get('mistake_rate', 0.07)

            logger.info("Configuration values loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration values: {e}")
            self.console.value = f"Error loading configuration: {e}\n"

    async def save_configuration_direct(self, widget):
        """Save configuration values directly to config.json."""
        try:
            # Get configuration path
            config_path = self.action_simulator._get_config_path()

            # Read current configuration
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Update code configuration
            if 'code' not in config:
                config['code'] = {}

            config['code']['language'] = self.language_input.value
            config['code']['indent_size'] = self.indent_input.value
            config['code']['max_line_length'] = self.max_line_input.value

            # Update typing speed configuration
            if 'typing_speed' not in config:
                config['typing_speed'] = {}

            config['typing_speed']['min'] = self.min_speed_input.value
            config['typing_speed']['max'] = self.max_speed_input.value
            config['typing_speed']['mistake_rate'] = self.mistake_input.value

            # Preserve line_break if it exists
            if 'line_break' not in config['typing_speed']:
                config['typing_speed']['line_break'] = [0.5, 1.0]

            # Write updated configuration
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)

            # Reload configuration in action simulator
            self.action_simulator.config = self.action_simulator._load_config()
            self.action_simulator._setup_from_config()

            # Show success message
            self.console.value = "✅ Configuration saved and reloaded successfully.\n"
            self.status_label.text = "Configuration saved"
            logger.info("Configuration updated successfully")

        except Exception as e:
            self.console.value = f"❌ Error saving configuration: {e}\n"
            logger.error(f"Error saving configuration: {e}")

    def setup_components(self):
        """Set up the application components."""
        self.action_simulator = ActionSimulator(self.console, self)
        self.key_handler = GlobalKeyHandler(self, self.action_simulator)
        self.simulation_task = None

        # Now that ActionSimulator is initialized, we can load configuration values
        self.load_configuration_values()

    async def choose_file(self, widget):
        """Allow the user to select a code file."""
        try:
            dialog = toga.OpenFileDialog(
                title="Select a Code File",
                file_types=["txt"]
            )
            file_path = await self.main_window.dialog(dialog)

            # Handle the file_path based on its type
            if file_path:
                # Convert PosixPath to string if needed
                if hasattr(file_path, 'resolve'):  # It's a Path object
                    self.selected_file = str(file_path.resolve())
                elif isinstance(file_path, list) and file_path:  # It's a list of paths
                    self.selected_file = str(file_path[0])
                else:  # It's already a string
                    self.selected_file = str(file_path)

                filename = os.path.basename(self.selected_file)
                self.file_display.text = f"Selected: {filename}"
                logger.info(f"Selected file: {self.selected_file}")
                self.status_label.text = f"File selected: {filename}"
            else:
                self.selected_file = None
                self.file_display.text = "Using default resources/code files"
                logger.info("No file selected; using default.")
                self.status_label.text = "Using default files"
        except Exception as e:
            self.console.value += f"Error selecting file: {str(e)}\n"
            logger.error(f"Error in choose_file: {e}")
            self.selected_file = None
            self.file_display.text = "Using default resources/code files"

    async def start_simulation(self, widget):
        """Start the simulation process."""
        if not self.action_simulator.loop_flag:
            try:
                self.console.value = "🚀 Starting simulation...\n"
                self.update_button_states(running=True)
                self.action_simulator.loop_flag = True
                self.status_label.text = "Simulation running"

                # Get the selected simulation mode
                selected_mode = self.mode_selector.value
                self.action_simulator.simulation_mode = selected_mode
                self.console.value += f"▶️ Mode: {selected_mode}\n"

                # Determine which file to use based on the selected mode and whether a file was chosen
                file_to_use = None
                if selected_mode in ["Typing Only", "Hybrid"]:
                    if self.selected_file and os.path.exists(self.selected_file):
                        file_to_use = self.selected_file
                        filename = os.path.basename(file_to_use)
                        self.console.value += f"📄 Using selected file: {filename}\n"
                        logger.info(f"Using selected file: {file_to_use}")
                    else:
                        self.console.value += "📄 No valid file selected. Using default code samples\n"
                        logger.info("No valid file selected, using default code samples")
                else:
                    self.console.value += "📄 File selection not applicable for this mode\n"
                    logger.info("File selection not applicable for this mode")

                # Start the simulation task
                if not self.simulation_task:
                    self.simulation_task = asyncio.create_task(self.run_continuous_simulation(file_to_use))
                logger.info("Simulation started successfully.")
            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                await self.stop_simulation(widget)

    async def run_continuous_simulation(self, file_to_use: Optional[str]):
        """Run the continuous simulation loop."""
        try:
            while self.action_simulator.loop_flag:
                # Determine which file to use
                if file_to_use and os.path.exists(file_to_use):
                    next_file = file_to_use
                    logger.debug(f"Using provided file: {next_file}")
                else:
                    next_file = self.action_simulator.get_next_code_file()
                    logger.debug(f"Using default file: {next_file}")

                if not next_file:
                    self.console.value += "❌ No code files found to simulate typing.\n"
                    await asyncio.sleep(2)
                    continue

                # Calculate typing time if applicable
                if self.action_simulator.simulation_mode in ["Typing Only", "Hybrid"]:
                    await self.action_simulator.calculate_typing_time(next_file)

                # Execute the simulation based on the selected mode
                if self.action_simulator.simulation_mode == "Typing Only":
                    self.console.value += "⌨️ Simulating typing...\n"
                    await self.action_simulator.simulate_typing(next_file)
                elif self.action_simulator.simulation_mode == "Tab Switching Only":
                    self.console.value += "🔄 Switching between applications...\n"
                    self.action_simulator.switch_window()
                    await asyncio.sleep(2)
                elif self.action_simulator.simulation_mode == "Hybrid":
                    self.console.value += "⌨️ Simulating typing...\n"
                    await self.action_simulator.simulate_typing(next_file)
                    self.console.value += "🔄 Switching between applications...\n"
                    self.action_simulator.switch_window()
                    await asyncio.sleep(2)
                elif self.action_simulator.simulation_mode == "Mouse and Command+Tab":
                    # Use the dedicated method for this simulation mode
                    await self.action_simulator.simulate_mouse_and_command_tab(duration=15)  # Run for 15 seconds

                filename = os.path.basename(next_file)
                self.console.value += f"\n✅ Finished simulating file: {filename}\n"
                self.console.value += "🔄 Cycle completed. Restarting...\n\n"
                self.status_label.text = "Cycle completed"
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            self.console.value += "⏹️ Simulation task cancelled.\n"
            self.status_label.text = "Simulation cancelled"
        except Exception as e:
            self.console.value += f"❌ Error during simulation: {str(e)}\n"
            self.status_label.text = "Error in simulation"
            logger.error(f"Error in continuous simulation: {e}")
            await self.stop_simulation(None)

    async def stop_simulation(self, widget):
        """Stop the simulation process."""
        if self.action_simulator.loop_flag:
            try:
                self.console.value += "⏹️ Stopping simulation...\n"
                self.action_simulator.loop_flag = False
                self.update_button_states(running=False)
                self.status_label.text = "Simulation stopped"
                if self.simulation_task:
                    self.simulation_task.cancel()
                    self.simulation_task = None
                logger.info("Simulation stopped successfully.")
            except Exception as e:
                logger.error(f"Error stopping simulation: {e}")

    def update_button_states(self, running: bool):
        """Update UI button states based on simulation status."""
        self.start_button.enabled = not running
        self.stop_button.enabled = running


def main():
    return CodeSimulator()
