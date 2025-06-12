===============
Code Simulator
===============

Code Simulator is a desktop application that simulates coding activity, including typing, application window switching, and mouse movements. It's built using the Toga_ GUI toolkit.

.. _Toga: https://toga.readthedocs.io/en/stable/

Features
--------
*   **Realistic Typing Simulation:** Types out content from text files, emulating human typing speed, mistakes, and pauses.
*   **Application Switching:** Simulates switching between different user-configured applications.
*   **Mouse Movement:** Can simulate random mouse movements and command-tab actions.
*   **Configurable:** Adjust typing speed, mistake rate, code formatting (language, indent), and target applications via JSON configuration files.
*   **Cross-Platform GUI:** Provides a graphical user interface for controlling simulations, viewing logs, and configuring settings.
*   **Multiple Simulation Modes:** Including "Typing Only", "Tab Switching Only", "Hybrid", and "Mouse and Command+Tab".

Setup and Running
-----------------
This project uses Briefcase_ for packaging and running.

.. _Briefcase: https://briefcase.readthedocs.io/en/stable/

1.  **Prerequisites:**
    *   Python 3.7+
    *   Ensure you have the necessary system dependencies for Toga and PyAutoGUI on your platform.
        *   **macOS:** You may need to grant Accessibility permissions for the application (or your terminal if running from source) for PyAutoGUI to control mouse and keyboard. Go to "System Settings > Privacy & Security > Accessibility".
        *   **Linux:** PyAutoGUI may require `scrot` for screenshots and X11 libraries (e.g., `libxtst-dev`, `python3-tk`, `python3-dev`). Refer to PyAutoGUI documentation for platform-specific setup. Toga's GTK backend will require GTK development libraries.
        *   **Windows:** Should generally work out of the box if Python is installed.

2.  **Install Project Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    python -m pip install -e .
    ```

3.  **Run in Developer Mode:**
    ```bash
    briefcase dev -r
    ```
    The `-r` flag will update dependencies if they've changed.

4.  **Package (Optional):**
    To build a distributable application:
    ```bash
    briefcase package
    ```
    Find the packaged application in the platform-specific directory within `build`.

Usage
-----
*   Launch the application.
*   Navigate to the "Configuration" tab to review or modify settings for typing speed, code style, and target applications (in `src/codesimulator/resources/applications.json`).
*   Go to the "Simulation" tab.
*   Select a simulation mode.
*   Optionally, choose a `.txt` file for typing simulation. If none is chosen, default samples will be used.
*   Click the "▶" (Start) button to begin the simulation.
*   Click the "⏹" (Stop) button to end the simulation.
*   Keyboard shortcuts: ⌘+S (Ctrl+S) to Start, ⌘+X (Ctrl+X) to Stop.
*   View logs and debug information in the "Logs" tab.

Troubleshooting
---------------
*   **PyAutoGUI Errors:** If simulation doesn't start or you see errors related to `pyautogui`, ensure permissions (macOS) or dependencies (Linux) are correctly set up. The application will attempt to guide you via messages in the "Logs" or "Simulation" console.
*   **Configuration Files:** Default `config.json` (for simulation settings) and `applications.json` (for app switching targets) are created in the `src/codesimulator/resources/` directory if not found. You can customize these.
