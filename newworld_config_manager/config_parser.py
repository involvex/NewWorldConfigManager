import xml.etree.ElementTree as ET
import os
import glob
from pathlib import Path
import shutil
import datetime

# For INI-style CFG files, you might use configparser
# import configparser

class ConfigParser:
    def __init__(self):
        self.new_world_config_dir = self._get_new_world_config_dir()
        if not self.new_world_config_dir:
            print("Warning: New World config directory not found.")

    def _get_new_world_config_dir(self) -> Path | None:
        """
        Attempts to find the New World configuration directory.
        Default path: %APPDATA%/AGS/New World
        """
        appdata_path = os.getenv('APPDATA')
        if appdata_path:
            nw_config_path = Path(appdata_path) / "AGS" / "New World"
            if nw_config_path.is_dir():
                print(f"Found New World config directory: {nw_config_path}")
                return nw_config_path
        # Fallback for non-Windows or if APPDATA is not set, though less likely for this game
        # On Linux, it might be ~/.config/AGS/New World or similar through Proton
        # For now, we focus on the standard Windows path.
        # TODO: Add platform-specific paths or allow user to specify path
        home_path = Path.home()
        # A common Proton path structure might be:
        # Path.home() / ".steam" / "steam" / "steamapps" / "compatdata" / "1063730" / "pfx" / "drive_c" / "users" / "steamuser" / "AppData" / "Roaming" / "AGS" / "New World"
        # This is complex and game/Proton version dependent. For now, we'll stick to the direct Windows path.
        print(f"Could not automatically determine New World config directory using APPDATA.")
        # As a direct example for the user's request, but this should be dynamic
        # For development/testing with a known path:
        # specific_user_path = Path("C:/Users/lukas/AppData/Roaming/AGS/New World")
        # if specific_user_path.is_dir():
        #     print(f"Using specific user path: {specific_user_path}")
        #     return specific_user_path
        return None

    def load_xml_config(self, filepath):
        """Loads an XML configuration file."""
        if not Path(filepath).is_file():
            print(f"Error: XML file not found at {filepath}")
            return None
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            print(f"Successfully loaded XML: {filepath}")
            # TODO: Process XML data into a more usable format
            return root
        except ET.ParseError as e:
            print(f"Error parsing XML file {filepath}: {e}")
            return None

    def save_xml_config(self, filepath: str, root_element: ET.Element) -> bool:
        """Saves an XML ElementTree root_element to the specified filepath."""
        if root_element is None: # Check if root_element is None
            print("Error: No XML data to save.")
            return False
        try:
            tree = ET.ElementTree(root_element)
            ET.indent(tree, space="  ", level=0) # For pretty printing
            tree.write(filepath, encoding="utf-8", xml_declaration=True)
            print(f"Successfully saved XML to: {filepath}")
            return True
        except Exception as e:
            print(f"Error saving XML file {filepath}: {e}")
            return False
    def _find_latest_rebindings_file(self) -> str | None:
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

    def load_rebindings_config(self):
        """Loads the New World rebindings XML configuration."""
        rebindings_file_path = self._find_latest_rebindings_file()
        if rebindings_file_path:
            return self.load_xml_config(rebindings_file_path)
        return None

    def load_user_settings_config(self) -> tuple[str, ET.Element | None] | None:
        """
        Attempts to load and parse usersettings.javsave as XML.
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
                print(f"Successfully parsed usersettings.javsave as XML: {javsave_path}")
                return str(javsave_path), root
            except ET.ParseError as e:
                print(f"Error parsing usersettings.javsave as XML: {e}")
                return str(javsave_path), None # Return path but None for root to indicate parsing failure
            except Exception as e:
                print(f"Error processing usersettings.javsave: {e}")
                return None
        else:
            print(f"usersettings.javsave not found at: {javsave_path}")
            return None

    def backup_config_folder(self) -> str | None:
        """
        Creates a timestamped backup of the entire New World config folder.
        The backup is placed in the parent directory of the config folder.
        e.g., if config is .../AGS/New World/, backup is .../AGS/New World_backup_YYYYMMDD_HHMMSS/
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
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    # TODO: Add methods for CFG and "javsave" files