# New World Config Manager

<p align="center">
  <img src="https://github.com/involvex/NewWorldConfigManager/blob/main/newworld_config_manager/ui/assets/logo.png" alt="New World Config Manager Logo" width="150"/>
</p>

**New World Config Manager** is a desktop application created by Involvex, designed to help you easily manage, edit, backup, and restore your New World game configuration files. It provides a user-friendly interface for handling complex XML settings, including key rebindings and various user preferences like UI colors.

## Features

*   **User-Friendly GUI:** Intuitive interface built with PyQt6 for managing complex XML configurations.
*   **Rebindings Editor:**
    *   Load, view, and modify your `rebindings_*.xml` files.
    *   Edit current key bindings.
    *   View default bindings for reference.
*   **User Settings Editor:**
    *   Load, view, and modify `usersettings.javsave` (parsed as XML).
    *   Edit various game settings.
    *   **Integrated Color Editor:** Visually edit RGBA color values (e.g., reticle colors) with sliders and a spinbox for alpha, complete with a live color preview.
*   **Automatic Config Detection:** Automatically locates your New World configuration directory (`%APPDATA%/AGS/New World`).
*   **Backup & Restore:**
    *   Create timestamped backups of your entire New World config folder.
    *   Restore settings from a chosen backup, overwriting current live settings safely.
*   **Safe Editing:**
    *   Changes are made in memory first.
    *   Option to reset current changes before saving.
    *   Prompts for backup before loading new configurations to prevent accidental data loss.
*   **Themed Interface:** A custom dark theme (blue and gold accents) for better visual appeal and usability.

## Screenshots

*(It's highly recommended to add a few screenshots here to showcase the application!)*

*   Example: Main window of the application.
*   Example: Editing key rebindings.
*   Example: Editing user settings, showing the color editor.

## Requirements

*   Python 3.x (developed with 3.9+)
*   PyQt6

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/involvex/NewWorldConfigManager.git
    cd NeWWorld-Config-Manager
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    # python -m venv venv
    # source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate    # On Windows

    pip install -r requirements.txt
    ```
    *(Ensure you have a `requirements.txt` file with `PyQt6` listed.)*

3.  **Run the application:**
    ```bash
    python main.py
    ```

## How to Use

1.  **Launch the Application:** Run `python main.py` from the project directory.
2.  **Load Configuration:**
    *   Click **"Load Rebindings Config"** to load and edit key bindings.
    *   Click **"Load User Settings (javsave)"** to load and edit general game settings.
    *   The application will prompt you to back up your settings before loading a configuration for the first time or when switching.
3.  **Edit Settings:**
    *   **Rebindings:** In the tree view, double-click or select an item in the "Current Binding" column to edit its value.
    *   **User Settings:**
        *   For text/numeric values: Double-click or select an item in the "Value" column to edit.
        *   For color values (identified by a color swatch icon): Use the integrated R, G, B sliders and Alpha (A) spinbox that appear in the "Value" column. The color preview icon will update live.
4.  **Save Changes:**
    *   Once you've made your desired changes, click **"Save Current Config"**. This will overwrite the original configuration file with your modifications. The "Reset Current Changes" button will become disabled.
5.  **Reset Changes:**
    *   If you want to discard any modifications made since the last load or save, click **"Reset Current Changes"**. This will reload the configuration from disk.
6.  **Backup Settings:**
    *   Click **"Backup Settings Now"** to create a full backup of your New World configuration folder.
    *   Backups are timestamped and stored in the parent directory of your New World config folder (e.g., `.../AGS/New World_backup_YYYYMMDD_HHMMSS/`).
7.  **Restore from Backup:**
    *   Click **"Restore from Backup"**.
    *   You will be prompted to select a backup folder.
    *   Confirm the restore operation. **Caution:** This will overwrite your current live New World settings with the contents of the selected backup.

## File Structure

```
NeWWorld-Config-Manager/
├── newworld_config_manager/    # Main application package
│   ├── ui/                     # UI related files (widgets, assets)
│   │   ├── assets/
│   │   │   └── logo.png        # Application logo
│   │   └── __init__.py
│   ├── __init__.py
│   ├── config_parser.py        # Logic for finding, loading, saving, backing up configs
│   └── main_window.py          # Main application window and UI logic
├── main.py                     # Entry point of the application
├── README.md                   # This file
├── requirements.txt            # Python package dependencies
└── .gitignore                  # Specifies intentionally untracked files that Git should ignore
```

## Troubleshooting

*   **"New World config directory not found":**
    *   Ensure New World has been run at least once to create its configuration files.
    *   The application primarily looks for the standard Windows path (`%APPDATA%/AGS/New World`). If your configuration is in a non-standard location (e.g., due to Proton on Linux, or a custom install), the tool might not find it automatically. Future versions may allow manual path specification.
*   **"Failed to parse usersettings.javsave as XML":**
    *   While `usersettings.javsave` often contains XML-like data, it might not always be perfectly valid XML or could be corrupted. If parsing fails, you might not be able to edit it with this tool. Restoring from a game backup or an older backup made by this tool might help.
*   **Application Icon Not Showing:**
    *   Ensure the `logo.png` file is correctly placed at `newworld_config_manager/ui/assets/logo.png`.

## Disclaimer

Modifying game configuration files can potentially lead to unexpected behavior if not done carefully. While this tool aims to provide a safe way to manage these settings, always consider backing up your settings before making significant changes. The "Backup Settings Now" feature is provided for this purpose. Use this tool at your own risk.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check issues page (if you have one).

## License

This project is open source. Please add a `LICENSE` file to specify the terms under which it is shared (e.g., MIT, GPL, Apache 2.0).

---

*Created by Involvex*