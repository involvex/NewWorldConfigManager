# New World Config Manager

A simple tool to manage configuration files for the game New World. 
This application allows users to view, edit, back up, and restore their game settings.

## Features

*   **Load and Edit Rebindings**: View and modify your keybindings (`rebindings.xml`).
*   **Load and Edit User Settings**: View and modify user settings, including colors with a visual editor (`usersettings.javsave`).
*   **Color Editor**: Easily edit RGBA color values using sliders for supported color settings.
*   **Backup Settings**: Create a timestamped backup of your entire New World configuration folder.
*   **Restore from Backup**: Restore your settings from a previously created backup.
*   **Reset Changes**: Discard any unsaved changes made in the current session.

## Prerequisites

*   Python 3.x (developed with 3.9+)
*   PyQt6: `pip install PyQt6`

## How to Run

1.  Ensure Python and PyQt6 are installed.
2.  Clone this repository or download the source code.
3.  Navigate to the root directory of the project in your terminal.
4.  Run the application using:
    ```bash
    python main.py
    ```
    or
    ```bash
    py -3 main.py
    ```

## Configuration File Locations

The application attempts to automatically find your New World configuration directory, typically located at:
`%APPDATA%\AGS\New World`

The main files managed are:
*   `rebindings.xml` (and its hashed variants like `rebindings_b*.xml`) for keybindings.
*   `savedata/usersettings.javsave` for general user settings.

## Disclaimer

Modifying game configuration files can potentially lead to unexpected behavior if not done carefully. While this tool aims to provide a safe way to manage these settings, always consider backing up your settings before making significant changes. The "Backup Settings Now" feature is provided for this purpose. Use this tool at your own risk.

## Created By

Involvex