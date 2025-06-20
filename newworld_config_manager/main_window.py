import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QMessageBox, QTreeWidget, QTreeWidgetItem, QFileDialog,
    QSlider, QDoubleSpinBox, QStyledItemDelegate, QStyleOptionViewItem) # Added QSlider, QDoubleSpinBox, QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtCore import Qt, pyqtSignal # Import pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon
from .config_parser import ConfigParser
from pathlib import Path # Ensure Path is imported
import xml.etree.ElementTree as ET # For type hinting and working with XML elements
import shutil # For restore from backup

class MainWindow(QMainWindow):
    class ColorEditorWidget(QWidget):
        """Custom widget for editing RGBA color values with sliders."""
        color_changed_signal = pyqtSignal(tuple) # (R, G, B, A) floats 0.0-1.0

        def __init__(self, initial_rgba_floats=(0.0, 0.0, 0.0, 1.0), parent=None):
            super().__init__(parent)
            self.rgba_floats = initial_rgba_floats

            layout = QHBoxLayout(self)
            layout.setContentsMargins(2, 2, 2, 2) # Small margins
            layout.setSpacing(3)

            self.sliders = {}
            self.value_labels = {} # To display current slider value

            # R, G, B Sliders
            for i, label_text in enumerate(["R", "G", "B"]):
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(255)
                slider.setValue(int(self.rgba_floats[i] * 255))
                slider.setFixedWidth(60) # Make sliders a bit smaller
                slider.valueChanged.connect(self._update_color_from_sliders)
                self.sliders[label_text] = slider
                
                val_label = QLabel(str(slider.value()))
                val_label.setFixedWidth(25)
                self.value_labels[label_text] = val_label

                layout.addWidget(QLabel(label_text + ":"))
                layout.addWidget(slider)
                layout.addWidget(val_label)

            # Alpha SpinBox
            layout.addWidget(QLabel("A:"))
            self.alpha_spinbox = QDoubleSpinBox()
            self.alpha_spinbox.setMinimum(0.0)
            self.alpha_spinbox.setMaximum(1.0)
            self.alpha_spinbox.setSingleStep(0.05)
            self.alpha_spinbox.setDecimals(2)
            self.alpha_spinbox.setValue(self.rgba_floats[3])
            self.alpha_spinbox.setFixedWidth(50)
            self.alpha_spinbox.valueChanged.connect(self._update_color_from_sliders)
            layout.addWidget(self.alpha_spinbox)

        def _update_color_from_sliders(self):
            r = self.sliders["R"].value() / 255.0
            g = self.sliders["G"].value() / 255.0
            b = self.sliders["B"].value() / 255.0
            a = self.alpha_spinbox.value()
            self.rgba_floats = (r, g, b, a)
            self.value_labels["R"].setText(str(self.sliders["R"].value()))
            self.value_labels["G"].setText(str(self.sliders["G"].value()))
            self.value_labels["B"].setText(str(self.sliders["B"].value()))
            self.color_changed_signal.emit(self.rgba_floats)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New World Config Manager - by Involvex")
        self.setGeometry(100, 100, 800, 600)  # Increased size for tree view
        
        # Set window icon
        icon_path = Path(__file__).parent / "ui" / "assets" / "logo.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        self.config_parser = ConfigParser()
        self.current_rebindings_root: ET.Element | None = None # To store the loaded XML root
        self.current_rebindings_filepath: str | None = None # To store the path of the loaded rebindings file
        self.item_id_to_rebind_element: dict[int, ET.Element] = {} # Maps tree item id to its XML rebind element

        self.current_usersettings_root: ET.Element | None = None
        self.current_usersettings_filepath: str | None = None
        self.item_id_to_usersetting_element: dict[int, ET.Element] = {} # Maps tree item id to its user setting <Class> element
        self.changes_made_in_current_config = False
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main vertical layout for the central widget
        main_layout = QVBoxLayout(self.central_widget)

        # Status bar
        self.statusBar = self.statusBar()
        self.status_label = QLabel("Welcome to New World Config Manager!") # For dynamic messages
        self.statusBar.addWidget(self.status_label, 1) # Stretch factor 1

        self.created_by_label = QLabel("Created by Involvex")
        self.created_by_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.statusBar.addPermanentWidget(self.created_by_label)

        self.action_status_label = QLabel("Load a configuration file to begin.") # For persistent status like loaded file
        self.action_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.action_status_label.font()
        font.setPointSize(font.pointSize() + 1) # Slightly larger
        self.action_status_label.setFont(font)
        main_layout.addWidget(self.action_status_label)

        # Horizontal layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10) # Add spacing between buttons
        self.load_rebindings_button = QPushButton("Load Rebindings Config")
        self.load_rebindings_button.clicked.connect(self.handle_load_rebindings)
        button_layout.addWidget(self.load_rebindings_button)

        self.load_user_settings_button = QPushButton("Load User Settings (javsave)")
        self.load_user_settings_button.clicked.connect(self.handle_load_user_settings)
        button_layout.addWidget(self.load_user_settings_button)

        self.backup_button = QPushButton("Backup Settings Now")
        self.backup_button.clicked.connect(self.handle_backup_settings)
        button_layout.addWidget(self.backup_button)

        self.restore_backup_button = QPushButton("Restore from Backup")
        self.restore_backup_button.clicked.connect(self.handle_restore_from_backup)
        self.restore_backup_button.setEnabled(self.config_parser.new_world_config_dir is not None)
        button_layout.addWidget(self.restore_backup_button)

        self.reset_changes_button = QPushButton("Reset Current Changes")
        self.reset_changes_button.clicked.connect(self.handle_reset_changes)
        self.reset_changes_button.setEnabled(False) # Initially disabled
        button_layout.addWidget(self.reset_changes_button)

        self.save_button = QPushButton("Save Current Config") # Changed button text
        self.save_button.clicked.connect(self.handle_save_current_config) # Changed handler
        self.save_button.setEnabled(False) # Disabled until a config is loaded
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)


        # Tree widget for displaying config
        self.config_tree_widget = QTreeWidget()
        self.config_tree_widget.setColumnCount(2)
        self.config_tree_widget.setHeaderLabels(["Name", "Value"])
        main_layout.addWidget(self.config_tree_widget)
        self.config_tree_widget.itemChanged.connect(self.handle_item_changed)

    def _populate_rebindings_tree(self, root_element: ET.Element):
        """
        Populates the QTreeWidget with rebindings data from the XML root element.
        Columns: "Action/Setting", "Current Value", "Default Value"
        """
        self.config_tree_widget.blockSignals(True) # Block signals during population
        self.config_tree_widget.clear()
        self.config_tree_widget.setColumnCount(3)
        self.config_tree_widget.setHeaderLabels(["Action/Setting", "Current Binding", "Default Binding"])
        self.item_id_to_rebind_element.clear() # Clear previous mapping

        if root_element is None:
            return

        for actionmap_element in root_element.findall('actionmap'):
            actionmap_name = actionmap_element.get('name', 'Unknown ActionMap')
            actionmap_item = QTreeWidgetItem(self.config_tree_widget)
            actionmap_item.setText(0, actionmap_name)
            
            font = actionmap_item.font(0)
            font.setBold(True)
            actionmap_item.setFont(0, font)
            actionmap_item.setExpanded(True) # Expand action maps by default

            for action_element in actionmap_element.findall('action'):
                action_name = action_element.get('name', 'Unknown Action')
                
                # Handle multiple rebinds per action if they exist
                rebinds = action_element.findall('rebind')
                if not rebinds: # Action might not have a rebind, or structure is different
                    action_row_item = QTreeWidgetItem(actionmap_item)
                    action_row_item.setText(0, f"  {action_name}") # Indent action name
                    action_row_item.setText(1, "N/A")
                    action_row_item.setText(2, "N/A")
                else:
                    for rebind_element in rebinds:
                        device = rebind_element.get('device', '')
                        input_val = rebind_element.get('input', '')
                        default_input_val = rebind_element.get('defaultInput', '')

                        action_row_item = QTreeWidgetItem(actionmap_item)
                        action_row_item.setText(0, f"  {action_name} ({device})")
                        action_row_item.setText(1, input_val)
                        # Make the "Current Binding" column (index 1) editable
                        action_row_item.setFlags(action_row_item.flags() | Qt.ItemFlag.ItemIsEditable)
                        action_row_item.setText(2, default_input_val)
                        self.item_id_to_rebind_element[id(action_row_item)] = rebind_element # Store mapping using item's id
        
        for i in range(self.config_tree_widget.columnCount()):
            self.config_tree_widget.resizeColumnToContents(i)
        self.config_tree_widget.blockSignals(False) # Unblock signals

    def _populate_generic_xml_tree(self, parent_item_or_tree, element: ET.Element):
        """
        Recursively adds generic XML elements and their attributes to the QTreeWidget.
        Columns: "Name", "Value"
        """
        # If the element is a "Class" with a "field" attribute, we treat it as a setting
        if element.tag == "Class" and "field" in element.attrib:
            field_name = element.get("field")
            value = element.get("value", "") # Default to empty string if no value attribute

            # Create a tree item for this setting
            setting_item = QTreeWidgetItem(parent_item_or_tree)
            setting_item.setText(0, field_name) # Show field name in the first column

            is_generic_color_candidate = "color" in field_name.lower()
            is_specific_reticle_color = field_name.lower() in ("m_reticletargetcolor", "m_reticlecolor")

            use_color_editor_widget = False
            parsed_rgba_floats = None

            # Try to parse value as RGBA if it looks like it could be one
            if " " in value: # A basic check for space-separated values
                try:
                    parts = [float(x) for x in value.split()]
                    if len(parts) == 4:
                        parsed_rgba_floats = tuple(parts)
                except ValueError:
                    parsed_rgba_floats = None # Parsing failed

            if is_specific_reticle_color:
                use_color_editor_widget = True
                # Default to green if specific reticle color and value is bad/missing
                if parsed_rgba_floats is None:
                    parsed_rgba_floats = (0.0, 1.0, 0.0, 1.0) 
                    # Update the XML element in memory immediately if we're applying a default
                    element.set('value', " ".join(map(str, parsed_rgba_floats)))
                    print(f"Applied default color {parsed_rgba_floats} to '{field_name}' due to missing/invalid value: '{value}'.")
            elif is_generic_color_candidate and parsed_rgba_floats is not None:
                # For other "color" fields, only use editor if value was successfully parsed as RGBA
                use_color_editor_widget = True

            if use_color_editor_widget:
                # Ensure parsed_rgba_floats is not None here; if specific_reticle_color, it's defaulted.
                # If generic, it must have been valid. Fallback just in case.
                editor_initial_rgba = parsed_rgba_floats if parsed_rgba_floats else (0.0,0.0,0.0,1.0)

                pixmap_preview = QPixmap(16, 16)
                q_color = QColor(int(editor_initial_rgba[0]*255), int(editor_initial_rgba[1]*255), int(editor_initial_rgba[2]*255), int(editor_initial_rgba[3]*255))
                pixmap_preview.fill(q_color)
                setting_item.setIcon(0, QIcon(pixmap_preview))
                
                editor_widget = MainWindow.ColorEditorWidget(initial_rgba_floats=editor_initial_rgba)
                self.config_tree_widget.setItemWidget(setting_item, 1, editor_widget)
                editor_widget.color_changed_signal.connect(
                    lambda new_rgba, item=setting_item: self.handle_color_editor_changed(item, new_rgba)
                )
            else: # Not using color editor
                setting_item.setText(1, value) # Show value in the second column
                setting_item.setFlags(setting_item.flags() | Qt.ItemFlag.ItemIsEditable)
            
            self.item_id_to_usersetting_element[id(setting_item)] = element # Map item to its <Class> element
            
            # We've processed this "Class as a setting", so we don't recurse into its attributes or children in the same way
            # If there are nested settings within this Class element (unlikely based on example), they'll be handled by recursive calls.

            # For "Class with field", children are processed as if they are direct children of the original parent_item_or_tree
            # to flatten the list of settings.
            for child_element in element:
                self._populate_generic_xml_tree(parent_item_or_tree, child_element)
            return # Important: stop further processing for this element

        # Handle elements that are NOT "Class with field" (e.g., ObjectStream, or Class without field if we want to show them)
        # We only create a tree item if it's not a 'Class' tag at all, or if it's a 'Class' tag
        # that we explicitly want to treat as a container (which current logic tries to avoid for display).
        # To strictly show only field/values, we might only want to process children of the root.
        # For now, let's create an item for non-Class tags or the root.
        item = None
        if element.tag != "Class" or parent_item_or_tree == self.config_tree_widget : # Show root or non-Class tags
            item = QTreeWidgetItem(parent_item_or_tree)
            item.setText(0, element.tag)
            if element.text and element.text.strip():
                item.setText(1, element.text.strip())

        # Recurse for children. If 'item' was created, children go under it.
        # Otherwise (e.g. for a 'Class' tag we skipped creating an item for), children are processed
        # as if they are direct children of parent_item_or_tree.
        for child_element in element:
            self._populate_generic_xml_tree(item if item is not None else parent_item_or_tree, child_element)


    def handle_load_rebindings(self, prompt_for_backup=True):
        if not self.config_parser.new_world_config_dir:
            QMessageBox.warning(self, "Config Directory Error", "New World config directory not found. Cannot load rebindings.")
            return

        if prompt_for_backup:
            reply = QMessageBox.question(self, "Backup Confirmation",
                                         "Do you want to back up your New World settings folder before loading the rebindings?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                         QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_backup()

        # Clear any user settings specific data if we are loading rebindings
        self.current_usersettings_root = None
        self.current_usersettings_filepath = None
        self.item_id_to_usersetting_element.clear()

        self.config_tree_widget.clear() # Clear previous content
        
        temp_rebindings_filepath = self.config_parser._find_latest_rebindings_file()
        if not temp_rebindings_filepath:
            self.status_label.setText("Failed to find rebindings XML file.")
            self.action_status_label.setText("Could not load rebindings.")
            self.config_tree_widget.clear()
            self.config_tree_widget.setColumnCount(2)
            self.config_tree_widget.setHeaderLabels(["Name", "Value"])
            QMessageBox.information(self, "Load Rebindings", "Could not find rebindings file. Check console for details.")
            self.save_button.setEnabled(False)
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
            self.current_rebindings_root = None
            self.current_rebindings_filepath = None
            return
        
        rebindings_data_root = self.config_parser.load_xml_config(temp_rebindings_filepath)

        if rebindings_data_root is not None:
            self.current_rebindings_filepath = temp_rebindings_filepath
            self.current_rebindings_root = rebindings_data_root
            self.action_status_label.setText(f"Rebindings loaded: {Path(self.current_rebindings_filepath).name}")
            self.status_label.setText("Rebindings XML loaded successfully!")
            self._populate_rebindings_tree(rebindings_data_root)
            self.save_button.setEnabled(True) # Enable save button
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
        else:
            self.status_label.setText(f"Failed to load rebindings XML from {Path(temp_rebindings_filepath).name}.")
            self.action_status_label.setText("Failed to load rebindings.")
            self.config_tree_widget.clear() # Clear tree on failure
            self.config_tree_widget.setColumnCount(2) # Reset to default if needed
            self.config_tree_widget.setHeaderLabels(["Name", "Value"])
            QMessageBox.information(self, "Load Rebindings", f"Could not load rebindings from {Path(temp_rebindings_filepath).name}. Check console.")
            self.save_button.setEnabled(False) # Disable save button
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
            self.current_rebindings_root = None
            self.current_rebindings_filepath = None

    def handle_load_user_settings(self, prompt_for_backup=True):
        if not self.config_parser.new_world_config_dir:
            QMessageBox.warning(self, "Config Directory Error", "New World config directory not found. Cannot load user settings.")
            return
        
        if prompt_for_backup:
            reply = QMessageBox.question(self, "Backup Confirmation",
                                     "Do you want to back up your New World settings folder before loading user settings?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                     QMessageBox.StandardButton.Yes)
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_backup()

        # Clear any rebindings specific data
        self.current_rebindings_root = None
        self.current_rebindings_filepath = None
        self.item_id_to_rebind_element.clear()

        self.config_tree_widget.clear() # Clear tree if showing other data
        self.item_id_to_usersetting_element.clear() # Clear previous mapping
        self.config_tree_widget.setColumnCount(2) # Reset to default columns
        self.config_tree_widget.setHeaderLabels(["Name", "Value"]) # Generic headers for XML

        self.config_tree_widget.blockSignals(True)
        try:
            result = self.config_parser.load_user_settings_config()
            if result:
                javsave_path, root_element = result
                self.current_usersettings_filepath = javsave_path # Store path even if root is None
                if root_element is not None:
                    self.action_status_label.setText(f"User Settings loaded: {Path(javsave_path).name}")
                    self.status_label.setText(f"Successfully parsed {Path(javsave_path).name} as XML.")
                    self.current_usersettings_root = root_element
                    self._populate_generic_xml_tree(self.config_tree_widget, root_element)
                    self.config_tree_widget.setColumnWidth(0, 250) # Name column
                    self.config_tree_widget.setColumnWidth(1, 350) # Value column (for sliders)
                    self.config_tree_widget.expandToDepth(1)
                    self.save_button.setEnabled(True) # Enable save for user settings
                    self.changes_made_in_current_config = False
                    self.reset_changes_button.setEnabled(False)
                else:
                    self.status_label.setText(f"Found {Path(javsave_path).name}, but failed to parse as XML. See console.")
                    self.action_status_label.setText(f"Error parsing {Path(javsave_path).name}.")
                    # Optionally display the path or an error message in the tree
                    error_item = QTreeWidgetItem(self.config_tree_widget)
                    error_item.setText(0, "Error")
                    error_item.setText(1, f"Could not parse {Path(javsave_path).name} as XML.")
                    self.save_button.setEnabled(False)
                    self.changes_made_in_current_config = False
                    self.reset_changes_button.setEnabled(False)
                    self.current_usersettings_root = None
                    # self.current_usersettings_filepath is already set
            else:
                self.status_label.setText("usersettings.javsave not found or could not be processed.")
                self.action_status_label.setText("Could not load user settings.")
                QMessageBox.information(self, "Load User Settings", "Could not find usersettings.javsave. Check console for details.")
                self.save_button.setEnabled(False)
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
                self.current_usersettings_root = None
                self.current_usersettings_filepath = None
        finally:
            self.config_tree_widget.blockSignals(False)

    
    def perform_backup(self):
        if not self.config_parser.new_world_config_dir:
            QMessageBox.critical(self, "Backup Error", "New World config directory not found. Cannot perform backup.")
            return False
        
        backup_path = self.config_parser.backup_config_folder()
        if backup_path:
            QMessageBox.information(self, "Backup Successful", f"Settings successfully backed up to:\n{backup_path}")
            return True
        else:
            QMessageBox.warning(self, "Backup Failed", "Failed to back up settings. Check console for details.")
            return False

    def handle_backup_settings(self):
        self.perform_backup()

    def handle_restore_from_backup(self):
        if not self.config_parser.new_world_config_dir:
            QMessageBox.critical(self, "Restore Error", "New World config directory not found. Cannot perform restore.")
            return

        backup_parent_dir = self.config_parser.new_world_config_dir.parent
        selected_backup_path_str = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder to Restore",
            str(backup_parent_dir) 
        )

        if not selected_backup_path_str:
            return 

        selected_backup_path = Path(selected_backup_path_str)
        
        reply = QMessageBox.warning(self, "Confirm Restore",
                                     f"This will ERASE your current New World settings in:\n"
                                     f"{self.config_parser.new_world_config_dir}\n"
                                     f"and replace them with the contents of:\n"
                                     f"{selected_backup_path}\n\n"
                                     f"This operation cannot be undone easily. Are you absolutely sure?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                                     QMessageBox.StandardButton.Cancel) 

        if reply == QMessageBox.StandardButton.Cancel:
            return

        target_dir = self.config_parser.new_world_config_dir
        try:
            if not target_dir.is_dir():
                target_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"Attempting to remove directory: {target_dir}")
            shutil.rmtree(target_dir)
            print(f"Successfully removed directory: {target_dir}")
            
            print(f"Attempting to copy from {selected_backup_path} to {target_dir}")
            shutil.copytree(selected_backup_path, target_dir)
            print(f"Successfully copied backup to: {target_dir}")

            QMessageBox.information(self, "Restore Successful",
                                    f"Successfully restored settings from:\n{selected_backup_path}\n"
                                    f"to:\n{target_dir}\n\n"
                                    "Your active configuration in this tool has been cleared. "
                                    "Please load a configuration file to see the restored settings.")

            self.config_tree_widget.clear()
            self.current_rebindings_root = None; self.current_rebindings_filepath = None
            self.item_id_to_rebind_element.clear()
            self.current_usersettings_root = None; self.current_usersettings_filepath = None
            self.item_id_to_usersetting_element.clear()
            
            self.save_button.setEnabled(False)
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
            self.action_status_label.setText("Backup restored. Load a config file to view.")
            self.status_label.setText("Settings restored successfully from backup.")

        except Exception as e:
            QMessageBox.critical(self, "Restore Failed", f"An error occurred during restore: {e}\nCheck the New World config directory manually.")
            self.status_label.setText("Restore failed. Check console. Config directory may be affected.")
            print(f"Error during restore: {e}")

    def handle_item_changed(self, item: QTreeWidgetItem, column: int):
        """
        Called when a QTreeWidget item is changed by the user.
        Updates the in-memory XML data.
        """
        item_id = id(item)
        if column == 1 and not self.config_tree_widget.itemWidget(item, 1): # Only if no custom widget
            if item_id in self.item_id_to_rebind_element:
                rebind_element = self.item_id_to_rebind_element[item_id]
                new_value = item.text(1)
                rebind_element.set('input', new_value)
                action_description = item.text(0).strip()
                print(f"Updated rebind action '{action_description}' to '{new_value}' in memory.")
                self.changes_made_in_current_config = True
                self.reset_changes_button.setEnabled(True)
                self.status_label.setText("Changes made. Click 'Save Current Config' or 'Reset Current Changes'.")
            elif item_id in self.item_id_to_usersetting_element:
                usersetting_element = self.item_id_to_usersetting_element[item_id]
                new_value_text = item.text(1)

                # If it was a color, we need to parse the R: G: B: A: text back to "R G B A" string
                # or handle direct numeric input. For simplicity, let's assume direct input for now
                # or that the user edits the "Raw: R G B A" part if they want to change color text.
                # A more robust solution would involve custom delegates or parsing the "R: G: B: A:" format.
                
                # For now, let's assume the user edits the raw numeric string if it's a color.
                # If the text starts with " R:", it means it's our formatted color string.
                # We'd ideally parse this back or provide a better editing widget.
                # This part needs to be more robust for color editing.
                # For now, we'll just take the text as is.
                # A simple approach: if it was a color, the user might have edited the raw part.
                # Or, they might have typed new numbers.

                usersetting_element.set('value', new_value_text.strip()) # Update the 'value' attribute
                field_name = usersetting_element.get('field')
                print(f"Updated user setting '{field_name}' to '{new_value_text.strip()}' in memory.")
                self.changes_made_in_current_config = True
                self.reset_changes_button.setEnabled(True)
                self.status_label.setText("Changes made. Click 'Save Current Config' or 'Reset Current Changes'.")

    def handle_color_editor_changed(self, item: QTreeWidgetItem, new_rgba_floats: tuple):
        """Handles changes from the ColorEditorWidget."""
        item_id = id(item)
        if item_id in self.item_id_to_usersetting_element:
            usersetting_element = self.item_id_to_usersetting_element[item_id]
            # Format the float tuple back to a space-separated string for XML
            new_value_str = " ".join(map(str, new_rgba_floats))
            usersetting_element.set('value', new_value_str)
            
            field_name = usersetting_element.get('field')
            print(f"Updated user setting (color) '{field_name}' to '{new_value_str}' in memory via sliders.")
            self.changes_made_in_current_config = True
            self.reset_changes_button.setEnabled(True)
            self.status_label.setText("Color changes made. Click 'Save Current Config' or 'Reset Current Changes'.")
            # Update the icon preview
            pixmap_preview = QPixmap(16,16)
            color = QColor(int(new_rgba_floats[0]*255), int(new_rgba_floats[1]*255), int(new_rgba_floats[2]*255), int(new_rgba_floats[3]*255))
            pixmap_preview.fill(color)
            item.setIcon(0, QIcon(pixmap_preview))

    def handle_reset_changes(self):
        if not (self.current_rebindings_filepath or self.current_usersettings_filepath):
            QMessageBox.information(self, "Reset Changes", "No configuration is currently loaded to reset.")
            return

        reply = QMessageBox.question(self, "Confirm Reset",
                                     "Are you sure you want to discard all current changes and reload the configuration from disk?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        # Check which type of config is loaded. current_..._root being not None is a good indicator.
        if self.current_rebindings_root is not None and self.current_rebindings_filepath is not None:
            self.handle_load_rebindings(prompt_for_backup=False)
        elif self.current_usersettings_root is not None and self.current_usersettings_filepath is not None:
            self.handle_load_user_settings(prompt_for_backup=False)
        elif self.current_usersettings_filepath is not None: # Case: user settings file found but failed to parse
            self.handle_load_user_settings(prompt_for_backup=False)
        else:
            self.status_label.setText("Could not determine which configuration to reset.")
            self.action_status_label.setText("Reset failed: No active configuration.")
            # This state should ideally not be reached if the first check passed
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
            return
        # The load functions will set changes_made_in_current_config to False, 
        # disable reset_changes_button, and update the label.

    def handle_save_current_config(self):
        if self.current_rebindings_root and self.current_rebindings_filepath:
            success = self.config_parser.save_xml_config(self.current_rebindings_filepath, self.current_rebindings_root)
            if success:
                QMessageBox.information(self, "Save Successful", f"Rebindings saved to:\n{self.current_rebindings_filepath}")
                self.action_status_label.setText(f"Rebindings saved: {Path(self.current_rebindings_filepath).name}")
                self.status_label.setText("Rebindings saved successfully.")
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
            else:
                QMessageBox.critical(self, "Save Failed", "Failed to save rebindings. Check console for details.")
        elif self.current_usersettings_root and self.current_usersettings_filepath:
            success = self.config_parser.save_xml_config(self.current_usersettings_filepath, self.current_usersettings_root)
            if success:
                QMessageBox.information(self, "Save Successful", f"User settings saved to:\n{self.current_usersettings_filepath}")
                self.action_status_label.setText(f"User settings saved: {Path(self.current_usersettings_filepath).name}")
                self.status_label.setText("User settings saved successfully.")
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
            else:
                QMessageBox.critical(self, "Save Failed", "Failed to save user settings. Check console for details.")
        else:
            QMessageBox.warning(self, "Save Error", "No configuration data loaded to save.")