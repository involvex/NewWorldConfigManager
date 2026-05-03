"""Configuration parser for New World game settings.

Handles loading, saving, and backing up New World configuration files
including rebindings XML, user settings, and preload settings.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import datetime
import glob
import os


class ConfigParser:
    """Parses and manages New World game configuration files."""

    def __init__(self):
        self.new_world_config_dir = self._get_new_world_config_dir()
        if not self.new_world_config_dir:
            print("Warning: New World config directory not found.")

    def _get_new_world_config_dir(self) -> Path | None:
        """Attempts to find the New World configuration directory.

        Default path: %APPDATA%/AGS/New World
        """
        appdata_path = os.getenv("APPDATA")
        if appdata_path:
            nw_config_path = Path(appdata_path) / "AGS" / "New World"
            if nw_config_path.is_dir():
                print(f"Found New World config directory: {nw_config_path}")
                return nw_config_path
        # Fallback for non-Windows or if APPDATA is not set, though less
        # likely for this game. On Linux, it might be
        # ~/.config/AGS/New World or similar through Proton.
        print("Could not automatically determine New World config directory.")
        return None

    def load_xml_config(self, filepath: str) -> ET.Element | None:
        """Loads an XML configuration file."""
        if not Path(filepath).is_file():
            print(f"Error: XML file not found at {filepath}")
            return None
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            print(f"Successfully loaded XML: {filepath}")
            return root
        except ET.ParseError as exc:
            print(f"Error parsing XML file {filepath}: {exc}")
            return None

    def save_xml_config(self, filepath: str, root_element: ET.Element) -> bool:
        """Saves an XML ElementTree root_element to the specified filepath."""
        if root_element is None:
            print("Error: No XML data to save.")
            return False
        try:
            tree = ET.ElementTree(root_element)
            ET.indent(tree, space="  ", level=0)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            print(f"Successfully saved XML to: {filepath}")
            return True
        except (OSError, ET.ParseError) as exc:
            print(f"Error saving XML file {filepath}: {exc}")
            return False

    def _find_latest_rebindings_file(self) -> str | None:
        """Finds the most recent rebindings file."""
        if not self.new_world_config_dir:
            return None

        pattern = str(self.new_world_config_dir / "rebindings_b*.xml")
        hashed_files = glob.glob(pattern)

        latest_file = None
        latest_mtime = 0

        if hashed_files:
            for f_path_str in hashed_files:
                f_path = Path(f_path_str)
                mtime = f_path.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = str(f_path)
            print(f"Found latest hashed rebindings: {latest_file}")
            return latest_file

        # If no hashed files, check for the generic rebindings.xml
        generic_rebindings = self.new_world_config_dir / "rebindings.xml"
        if generic_rebindings.is_file():
            print(f"Found generic rebindings: {generic_rebindings}")
            return str(generic_rebindings)

        print("No rebindings file found.")
        return None

    def load_rebindings_config(self) -> ET.Element | None:
        """Loads the New World rebindings XML configuration."""
        rebindings_file_path = self._find_latest_rebindings_file()
        if rebindings_file_path:
            return self.load_xml_config(rebindings_file_path)
        return None

    def load_user_settings_config(self) -> tuple[str, ET.Element | None] | None:
        """Attempts to load and parse usersettings.javsave as XML.

        Returns a tuple of (filepath, root_element) if successful.
        Returns None if the file cannot be read.
        """
        if not self.new_world_config_dir:
            print("Cannot load user settings: New World config directory not found.")
            return None
        javsave_path = self.new_world_config_dir / "savedata" / "usersettings.javsave"

        if javsave_path.is_file():
            print(f"Found usersettings.javsave at: {javsave_path}")
            try:
                # Attempt to parse directly as XML
                tree = ET.parse(javsave_path)
                root = tree.getroot()
                print(
                    f"Successfully parsed usersettings.javsave as XML: {javsave_path}"
                )
                return str(javsave_path), root
            except ET.ParseError as exc:
                print(f"Error parsing usersettings.javsave as XML: {exc}")
                return str(javsave_path), None
            except OSError as exc:
                print(f"Error processing usersettings.javsave: {exc}")
                return None
        print(f"usersettings.javsave not found at: {javsave_path}")
        return None

    def find_latest_rebindings_file(self) -> str | None:
        """Public wrapper for _find_latest_rebindings_file."""
        return self._find_latest_rebindings_file()

    def backup_config_folder(self) -> str | None:
        """Creates a timestamped backup of the entire New World config folder.

        The backup is placed in the parent directory of the config folder.
        e.g., if config is .../AGS/New World/,
        backup is .../AGS/New World_backup_YYYYMMDD_HHMMSS/

        Returns the path to the backup folder if successful, None otherwise.
        """
        if not self.new_world_config_dir or not self.new_world_config_dir.is_dir():
            print("Error: New World config directory not found or is not a directory.")
            return None

        backup_parent_dir = self.new_world_config_dir.parent
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder_name = f"{self.new_world_config_dir.name}_backup_{timestamp}"
        backup_path = backup_parent_dir / backup_folder_name

        try:
            shutil.copytree(self.new_world_config_dir, backup_path)
            print(f"Successfully backed up config folder to: {backup_path}")
            return str(backup_path)
        except OSError as exc:
            print(f"Error creating backup: {exc}")
            return None

    def load_preload_settings(self) -> dict[str, str] | None:
        """Loads user_preload_settings.cfg as key=value pairs.

        Returns dict of settings or None if file not found.
        """
        if not self.new_world_config_dir:
            print("Cannot load preload settings: config directory not found.")
            return None
        cfg_path = Path(self.new_world_config_dir) / "user_preload_settings.cfg"
        if not cfg_path.is_file():
            print(f"user_preload_settings.cfg not found at: {cfg_path}")
            return None
        settings = {}
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("--"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            settings[key.strip()] = value.strip()
            print(f"Successfully loaded preload settings: {cfg_path}")
            return settings
        except OSError as exc:
            print(f"Error reading preload settings: {exc}")
            return None

    def save_preload_settings(self, settings: dict[str, str]) -> bool:
        """Saves user_preload_settings.cfg from key=value dict.

        Returns True on success, False on failure.
        """
        if not self.new_world_config_dir:
            print("Cannot save preload settings: config directory not found.")
            return False
        cfg_path = Path(self.new_world_config_dir) / "user_preload_settings.cfg"
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write("-- User Preload Settings\n")
                for key, value in settings.items():
                    f.write(f"{key}={value}\n")
            print(f"Successfully saved preload settings: {cfg_path}")
            return True
        except OSError as exc:
            print(f"Error writing preload settings: {exc}")
            return False
