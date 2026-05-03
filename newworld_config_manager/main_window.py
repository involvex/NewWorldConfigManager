"""Main application window for New World Config Manager."""

import xml.etree.ElementTree as ET
import shutil
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QSlider,
    QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QIcon

from .config_parser import ConfigParser


@dataclass
class _AppState:
    """Container for main window state references."""

    current_rebindings_root: ET.Element | None = None
    current_rebindings_filepath: str | None = None
    item_id_to_rebind_element: dict[int, ET.Element] = None
    current_usersettings_root: ET.Element | None = None
    current_usersettings_filepath: str | None = None
    item_id_to_usersetting_element: dict[int, ET.Element] = None

    def __post_init__(self):
        if self.item_id_to_rebind_element is None:
            self.item_id_to_rebind_element = {}
        if self.item_id_to_usersetting_element is None:
            self.item_id_to_usersetting_element = {}


class MainWindow(QMainWindow):
    """Main window for the New World Config Manager application."""

    class ColorEditorWidget(QWidget):
        """Custom widget for editing RGBA color values with sliders."""

        color_changed_signal = pyqtSignal(tuple)  # (R, G, B, A) floats 0.0-1.0

        def __init__(self, initial_rgba_floats=(0.0, 0.0, 0.0, 1.0), parent=None):
            super().__init__(parent)
            self.rgba_floats = initial_rgba_floats

            layout = QHBoxLayout(self)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(3)

            self.sliders = {}
            self.value_labels = {}

            for label_text in ["R", "G", "B"]:
                i = ["R", "G", "B"].index(label_text)
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(255)
                slider.setValue(int(self.rgba_floats[i] * 255))
                slider.setFixedWidth(60)
                slider.valueChanged.connect(self._update_color_from_sliders)
                self.sliders[label_text] = slider

                val_label = QLabel(str(slider.value()))
                val_label.setFixedWidth(25)
                self.value_labels[label_text] = val_label

                layout.addWidget(QLabel(label_text + ":"))
                layout.addWidget(slider)
                layout.addWidget(val_label)

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
            """Update color from slider values and emit signal."""
            r = self.sliders["R"].value() / 255.0
            g = self.sliders["G"].value() / 255.0
            b = self.sliders["B"].value() / 255.0
            a = self.alpha_spinbox.value()
            self.rgba_floats = (r, g, b, a)
            self.value_labels["R"].setText(str(self.sliders["R"].value()))
            self.value_labels["G"].setText(str(self.sliders["G"].value()))
            self.value_labels["B"].setText(str(self.sliders["B"].value()))
            self.color_changed_signal.emit(self.rgba_floats)

        def get_rgba(self):
            """Get current RGBA values."""
            return self.rgba_floats

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New World Config Manager - by Involvex")
        self.setGeometry(100, 100, 800, 600)

        self.config_parser = ConfigParser()
        self.state = _AppState()
        self.changes_made_in_current_config = False

        self._setup_ui()
        self._setup_button_bar()

    def _setup_ui(self):
        """Set up the main user interface layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        self.statusBar().addWidget(QLabel("Welcome to New World Config Manager!"), 1)

        created_by = QLabel("Created by Involvex")
        created_by.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.statusBar().addPermanentWidget(created_by)

        self.action_status_label = QLabel("Load a configuration file to begin.")
        self.action_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.action_status_label.font()
        font.setPointSize(font.pointSize() + 1)
        self.action_status_label.setFont(font)
        main_layout.addWidget(self.action_status_label)

        self.config_tree_widget = QTreeWidget()
        self.config_tree_widget.setColumnCount(2)
        self.config_tree_widget.setHeaderLabels(["Name", "Value"])
        self.config_tree_widget.itemChanged.connect(self.handle_item_changed)
        main_layout.addWidget(self.config_tree_widget)

    def _setup_button_bar(self):
        """Set up the button bar with action buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        buttons = [
            ("Load Rebindings Config", self.handle_load_rebindings),
            ("Load User Settings (javsave)", self.handle_load_user_settings),
            ("Backup Settings Now", self.handle_backup_settings),
            ("Restore from Backup", self.handle_restore_from_backup),
            ("Reset Current Changes", self.handle_reset_changes),
            ("Save Current Config", self.handle_save_current_config),
        ]

        self.restore_backup_button = None
        self.reset_changes_button = None
        self.save_button = None

        for text, slot in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            button_layout.addWidget(btn)

            if text == "Restore from Backup":
                btn.setEnabled(self.config_parser.new_world_config_dir is not None)
                self.restore_backup_button = btn
            elif text == "Reset Current Changes":
                btn.setEnabled(False)
                self.reset_changes_button = btn
            elif text == "Save Current Config":
                btn.setEnabled(False)
                self.save_button = btn

        layout = self.central_widget.layout()
        layout.addLayout(button_layout)

    def _populate_rebindings_tree(self, root_element: ET.Element):
        """Populates the QTreeWidget with rebindings data from XML root element."""
        self.config_tree_widget.blockSignals(True)
        self.config_tree_widget.clear()
        self.config_tree_widget.setColumnCount(3)
        self.config_tree_widget.setHeaderLabels(
            ["Action/Setting", "Current Binding", "Default Binding"]
        )
        self.state.item_id_to_rebind_element.clear()

        if root_element is None:
            self.config_tree_widget.blockSignals(False)
            return

        for actionmap_element in root_element.findall("actionmap"):
            actionmap_name = actionmap_element.get("name", "Unknown ActionMap")
            actionmap_item = QTreeWidgetItem(self.config_tree_widget)
            actionmap_item.setText(0, actionmap_name)
            font = actionmap_item.font(0)
            font.setBold(True)
            actionmap_item.setFont(0, font)
            actionmap_item.setExpanded(True)

            for action_element in actionmap_element.findall("action"):
                action_name = action_element.get("name", "Unknown Action")
                rebinds = action_element.findall("rebind")

                if not rebinds:
                    action_row_item = QTreeWidgetItem(actionmap_item)
                    action_row_item.setText(0, f"  {action_name}")
                    action_row_item.setText(1, "N/A")
                    action_row_item.setText(2, "N/A")
                    continue

                for rebind_element in rebinds:
                    device = rebind_element.get("device", "")
                    input_val = rebind_element.get("input", "")
                    default_input_val = rebind_element.get("defaultInput", "")

                    action_row_item = QTreeWidgetItem(actionmap_item)
                    action_row_item.setText(0, f"  {action_name} ({device})")
                    action_row_item.setText(1, input_val)
                    action_row_item.setFlags(
                        action_row_item.flags() | Qt.ItemFlag.ItemIsEditable
                    )
                    action_row_item.setText(2, default_input_val)
                    self.state.item_id_to_rebind_element[id(action_row_item)] = (
                        rebind_element
                    )

        for i in range(self.config_tree_widget.columnCount()):
            self.config_tree_widget.resizeColumnToContents(i)
        self.config_tree_widget.blockSignals(False)

    def _populate_generic_xml_tree(self, parent_item_or_tree, element: ET.Element):
        """Recursively adds generic XML elements to QTreeWidget."""
        if element.tag == "Class" and "field" in element.attrib:
            self._process_class_field_setting(parent_item_or_tree, element)
            return

        item = None
        if element.tag != "Class" or parent_item_or_tree == self.config_tree_widget:
            item = QTreeWidgetItem(parent_item_or_tree)
            item.setText(0, element.tag)
            if element.text and element.text.strip():
                item.setText(1, element.text.strip())

        for child_element in element:
            self._populate_generic_xml_tree(
                item if item is not None else parent_item_or_tree, child_element
            )

    def _process_class_field_setting(self, parent_item_or_tree, element: ET.Element):
        """Process a Class element with a field attribute as a setting."""
        field_name = element.get("field")
        value = element.get("value", "")

        use_color_editor_widget = False
        parsed_rgba_floats = None

        if " " in value:
            try:
                parts = [float(x) for x in value.split()]
                if len(parts) == 4:
                    parsed_rgba_floats = tuple(parts)
            except ValueError:
                pass

        is_specific_reticle_color = field_name.lower() in (
            "m_reticletargetcolor",
            "m_reticlecolor",
        )
        is_generic_color_candidate = (
            "color" in field_name.lower() and parsed_rgba_floats is not None
        )

        if is_specific_reticle_color:
            use_color_editor_widget = True
            if parsed_rgba_floats is None:
                parsed_rgba_floats = (0.0, 1.0, 0.0, 1.0)
                element.set("value", " ".join(map(str, parsed_rgba_floats)))
        elif is_generic_color_candidate:
            use_color_editor_widget = True

        setting_item = QTreeWidgetItem(parent_item_or_tree)
        setting_item.setText(0, field_name)

        if use_color_editor_widget:
            editor_initial_rgba = (
                parsed_rgba_floats if parsed_rgba_floats else (0.0, 0.0, 0.0, 1.0)
            )
            self._setup_color_editor(setting_item, element, editor_initial_rgba)
        else:
            setting_item.setText(1, value)
            setting_item.setFlags(setting_item.flags() | Qt.ItemFlag.ItemIsEditable)

        self.state.item_id_to_usersetting_element[id(setting_item)] = element

        for child_element in element:
            self._populate_generic_xml_tree(parent_item_or_tree, child_element)

    def _setup_color_editor(self, item, _element, initial_rgba_floats):
        """Set up color editor widget for a tree item.

        Args:
            item: The QTreeWidgetItem being edited.
            _element: The XML element associated with this setting.
            initial_rgba_floats: Initial RGBA color values (0.0-1.0).
        """
        pixmap_preview = QPixmap(16, 16)
        q_color = QColor(
            int(initial_rgba_floats[0] * 255),
            int(initial_rgba_floats[1] * 255),
            int(initial_rgba_floats[2] * 255),
            int(initial_rgba_floats[3] * 255),
        )
        pixmap_preview.fill(q_color)
        item.setIcon(0, QIcon(pixmap_preview))

        editor_widget = self.ColorEditorWidget(initial_rgba_floats=initial_rgba_floats)
        self.config_tree_widget.setItemWidget(item, 1, editor_widget)
        editor_widget.color_changed_signal.connect(
            lambda new_rgba, it=item: self.handle_color_editor_changed(it, new_rgba)
        )

    def _show_load_failure(self, status_msg, action_msg):
        """Show load failure state."""
        self.status_label.setText(status_msg)
        self.action_status_label.setText(action_msg)
        self.config_tree_widget.clear()
        self.config_tree_widget.setColumnCount(2)
        self.config_tree_widget.setHeaderLabels(["Name", "Value"])
        QMessageBox.information(self, "Load Failed", status_msg + " Check console.")
        self.save_button.setEnabled(False)
        self.changes_made_in_current_config = False
        self.reset_changes_button.setEnabled(False)
        self.state.current_rebindings_root = None
        self.state.current_rebindings_filepath = None

    def _load_preload_settings(self):
        """Load preload settings and update UI."""
        settings = self.config_parser.load_preload_settings()
        if settings:
            self.state.preload_settings = (
                settings  # pylint: disable=attribute-defined-outside-init
            )
            self.preload_width.blockSignals(True)
            self.preload_height.blockSignals(True)
            self.preload_fullscreen.blockSignals(True)
            self.preload_fullscreen_window.blockSignals(True)
            self.preload_width.setValue(float(settings.get("r_Width", 1920)))
            self.preload_height.setValue(float(settings.get("r_Height", 1080)))
            self.preload_fullscreen.setValue(float(settings.get("r_Fullscreen", 1)))
            self.preload_fullscreen_window.setValue(
                float(settings.get("r_fullscreenWindow", 0))
            )
            self.preload_width.blockSignals(False)
            self.preload_height.blockSignals(False)
            self.preload_fullscreen.blockSignals(False)
            self.preload_fullscreen_window.blockSignals(False)
            self.preload_group.setEnabled(True)
            self.preload_save_btn.setEnabled(False)
            return True
        return False

    def _on_preload_changed(self):
        """Mark preload settings as changed."""
        self.preload_save_btn.setEnabled(True)

    def handle_load_rebindings(self, prompt_for_backup=True):
        """Handle loading rebindings configuration."""
        if not self.config_parser.new_world_config_dir:
            QMessageBox.warning(
                self,
                "Config Directory Error",
                "New World config directory not found. Cannot load rebindings.",
            )
            return

        if prompt_for_backup:
            reply = QMessageBox.question(
                self,
                "Backup Confirmation",
                "Do you want to back up your New World settings folder "
                "before loading the rebindings?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_backup()

        self.state.current_usersettings_root = None
        self.state.current_usersettings_filepath = None
        self.state.item_id_to_usersetting_element.clear()
        self.config_tree_widget.clear()
        self._clear_search()

        filepath = self.config_parser.find_latest_rebindings_file()
        if not filepath:
            self._show_load_failure(
                "Could not find rebindings file.",
                "Could not load rebindings.",
            )
            return

        root = self.config_parser.load_xml_config(filepath)

        if root is not None:
            self.state.current_rebindings_filepath = filepath
            self.state.current_rebindings_root = root
            self.action_status_label.setText(
                f"Rebindings loaded: {Path(filepath).name}"
            )
            self.status_label.setText("Rebindings XML loaded successfully!")
            self._populate_rebindings_tree(root)
            self.save_button.setEnabled(True)
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
        else:
            self._show_load_failure(
                f"Could not load rebindings from {Path(filepath).name}.",
                "Failed to load rebindings.",
            )

    def handle_load_user_settings(self, prompt_for_backup=True):
        """Handle loading user settings configuration."""
        if not self.config_parser.new_world_config_dir:
            QMessageBox.warning(
                self,
                "Config Directory Error",
                "New World config directory not found." " Cannot load user settings.",
            )
            return

        if prompt_for_backup:
            reply = QMessageBox.question(
                self,
                "Backup Confirmation",
                "Do you want to back up your New World settings folder "
                "before loading user settings?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                return
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_backup()

        self.state.current_rebindings_root = None
        self.state.current_rebindings_filepath = None
        self.state.item_id_to_rebind_element.clear()
        self.config_tree_widget.clear()
        self._clear_search()
        self.state.item_id_to_usersetting_element.clear()
        self.config_tree_widget.setColumnCount(2)
        self.config_tree_widget.setHeaderLabels(["Name", "Value"])

        self.config_tree_widget.blockSignals(True)
        try:
            result = self.config_parser.load_user_settings_config()
            if not result:
                self.status_label.setText(
                    "usersettings.javsave not found or could not be processed."
                )
                self.action_status_label.setText("Could not load user settings.")
                QMessageBox.information(
                    self,
                    "Load Failed",
                    "Could not find usersettings.javsave."
                    " Check console for details.",
                )
                self.save_button.setEnabled(False)
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
                self.state.current_usersettings_root = None
                self.state.current_usersettings_filepath = None
                return

            javsave_path, root_element = result
            self.state.current_usersettings_filepath = javsave_path

            if root_element is not None:
                self.action_status_label.setText(
                    f"User Settings loaded: {Path(javsave_path).name}"
                )
                self.status_label.setText(
                    f"Successfully parsed {Path(javsave_path).name} as XML."
                )
                self.state.current_usersettings_root = root_element
                self._populate_generic_xml_tree(self.config_tree_widget, root_element)
                self.config_tree_widget.setColumnWidth(0, 250)
                self.config_tree_widget.setColumnWidth(1, 350)
                self.config_tree_widget.expandToDepth(1)
                self.save_button.setEnabled(True)
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
            else:
                self.status_label.setText(
                    f"Found {Path(javsave_path).name}, but failed to parse as XML."
                )
                self.action_status_label.setText(
                    f"Error parsing {Path(javsave_path).name}."
                )
                error_item = QTreeWidgetItem(self.config_tree_widget)
                error_item.setText(0, "Error")
                error_item.setText(
                    1, f"Could not parse {Path(javsave_path).name} as XML."
                )
                self.save_button.setEnabled(False)
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
                self.state.current_usersettings_root = None
        finally:
            self.config_tree_widget.blockSignals(False)

        # Load preload settings after loading user settings
        self._load_preload_settings()

    def perform_backup(self):
        """Perform a backup of the config folder."""
        if not self.config_parser.new_world_config_dir:
            QMessageBox.critical(
                self,
                "Backup Error",
                "New World config directory not found. Cannot perform backup.",
            )
            return False

        backup_path = self.config_parser.backup_config_folder()
        if backup_path:
            QMessageBox.information(
                self,
                "Backup Successful",
                f"Settings successfully backed up to:\\n{backup_path}",
            )
            return True
        QMessageBox.warning(
            self,
            "Backup Failed",
            "Failed to back up settings. Check console for details.",
        )
        return False

    def handle_backup_settings(self):
        """Handle backup settings request."""
        self.perform_backup()

    def handle_restore_from_backup(self):
        """Handle restore from backup request."""
        if not self.config_parser.new_world_config_dir:
            QMessageBox.critical(
                self,
                "Restore Error",
                "New World config directory not found." " Cannot perform restore.",
            )
            return

        backup_parent_dir = self.config_parser.new_world_config_dir.parent
        selected_backup_path_str = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder to Restore",
            str(backup_parent_dir),
        )

        if not selected_backup_path_str:
            return

        selected_backup_path = Path(selected_backup_path_str)

        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            f"This will ERASE your current New World settings in:\\n"
            f"{self.config_parser.new_world_config_dir}\\n"
            f"and replace them with the contents of:\\n"
            f"{selected_backup_path}\\n\\n"
            f"This operation cannot be undone easily. Are you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

        if reply == QMessageBox.StandardButton.Cancel:
            return

        target_dir = self.config_parser.new_world_config_dir
        try:
            if not target_dir.is_dir():
                target_dir.mkdir(parents=True, exist_ok=True)

            shutil.rmtree(target_dir)
            shutil.copytree(selected_backup_path, target_dir)

            QMessageBox.information(
                self,
                "Restore Successful",
                f"Successfully restored settings from:\\n"
                f"{selected_backup_path}\\n"
                f"to:\\n{target_dir}\\n\\n"
                "Your active configuration in this tool has been cleared. "
                "Please load a configuration file to see the restored settings.",
            )

            self.config_tree_widget.clear()
            self.state.current_rebindings_root = None
            self.state.current_rebindings_filepath = None
            self.state.item_id_to_rebind_element.clear()
            self.state.current_usersettings_root = None
            self.state.current_usersettings_filepath = None
            self.state.item_id_to_usersetting_element.clear()
            self.save_button.setEnabled(False)
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)
            self.action_status_label.setText(
                "Backup restored. Load a config file to view."
            )
            self.status_label.setText("Settings restored successfully from backup.")
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Restore Failed",
                f"An error occurred during restore: {exc}\\n"
                "Check the New World config directory manually.",
            )
            self.status_label.setText(
                "Restore failed. Check console. Config directory may be affected."
            )

    def handle_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle QTreeWidget item change."""
        item_id = id(item)
        if column == 1 and not self.config_tree_widget.itemWidget(item, 1):
            if item_id in self.state.item_id_to_rebind_element:
                rebind_element = self.state.item_id_to_rebind_element[item_id]
                new_value = item.text(1)
                rebind_element.set("input", new_value)
                self.changes_made_in_current_config = True
                self.reset_changes_button.setEnabled(True)
                self.status_label.setText(
                    "Changes made. Click 'Save Current Config' "
                    "or 'Reset Current Changes'."
                )
            elif item_id in self.state.item_id_to_usersetting_element:
                usersetting_element = self.state.item_id_to_usersetting_element[item_id]
                usersetting_element.set("value", item.text(1).strip())
                self.changes_made_in_current_config = True
                self.reset_changes_button.setEnabled(True)
                self.status_label.setText(
                    "Changes made. Click 'Save Current Config' "
                    "or 'Reset Current Changes'."
                )

    def handle_color_editor_changed(
        self, item: QTreeWidgetItem, new_rgba_floats: tuple
    ):
        """Handle color editor value change."""
        item_id = id(item)
        if item_id in self.state.item_id_to_usersetting_element:
            usersetting_element = self.state.item_id_to_usersetting_element[item_id]
            new_value_str = " ".join(map(str, new_rgba_floats))
            usersetting_element.set("value", new_value_str)
            pixmap_preview = QPixmap(16, 16)
            pixmap_preview.fill(
                QColor(
                    int(new_rgba_floats[0] * 255),
                    int(new_rgba_floats[1] * 255),
                    int(new_rgba_floats[2] * 255),
                    int(new_rgba_floats[3] * 255),
                )
            )
            item.setIcon(0, QIcon(pixmap_preview))
            self.changes_made_in_current_config = True
            self.reset_changes_button.setEnabled(True)
            self.status_label.setText(
                "Color changes made. Click 'Save Current Config' "
                "or 'Reset Current Changes'."
            )

    def handle_reset_changes(self):
        """Handle reset changes request."""
        if not (
            self.state.current_rebindings_filepath
            or self.state.current_usersettings_filepath
        ):
            QMessageBox.information(
                self, "Reset Changes", "No configuration is currently loaded."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Discard all current changes and reload the configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.No:
            return

        if (
            self.state.current_rebindings_root is not None
            and self.state.current_rebindings_filepath is not None
        ):
            self.handle_load_rebindings(prompt_for_backup=False)
        elif (
            self.state.current_usersettings_root is not None
            and self.state.current_usersettings_filepath is not None
        ):
            self.handle_load_user_settings(prompt_for_backup=False)
        elif self.state.current_usersettings_filepath is not None:
            self.handle_load_user_settings(prompt_for_backup=False)
        else:
            self.status_label.setText(
                "Could not determine which configuration to reset."
            )
            self.action_status_label.setText("Reset failed: No active configuration.")
            self.changes_made_in_current_config = False
            self.reset_changes_button.setEnabled(False)

    def handle_save_current_config(self):
        """Handle save current config request."""
        if (
            self.state.current_rebindings_root
            and self.state.current_rebindings_filepath
        ):
            success = self.config_parser.save_xml_config(
                self.state.current_rebindings_filepath,
                self.state.current_rebindings_root,
            )
            if success:
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"Rebindings saved to:\\n{self.state.current_rebindings_filepath}",
                )
                self.action_status_label.setText(
                    f"Rebindings saved: {Path(self.state.current_rebindings_filepath).name}"
                )
                self.status_label.setText("Rebindings saved successfully.")
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save rebindings. Check console for details.",
                )
        elif (
            self.state.current_usersettings_root
            and self.state.current_usersettings_filepath
        ):
            success = self.config_parser.save_xml_config(
                self.state.current_usersettings_filepath,
                self.state.current_usersettings_root,
            )
            if success:
                QMessageBox.information(
                    self,
                    "Save Successful",
                    f"User settings saved to:\\n{self.state.current_usersettings_filepath}",
                )
                self.action_status_label.setText(
                    f"User settings saved: {Path(self.state.current_usersettings_filepath).name}"
                )
                self.status_label.setText("User settings saved successfully.")
                self.changes_made_in_current_config = False
                self.reset_changes_button.setEnabled(False)
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save user settings. Check console for details.",
                )
        else:
            QMessageBox.warning(
                self, "Save Error", "No configuration data loaded to save."
            )
