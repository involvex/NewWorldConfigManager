import sys
from PyQt6.QtWidgets import QApplication
from newworld_config_manager.main_window import MainWindow

def run_app():
    """Initializes and runs the PyQt6 application."""
    app = QApplication(sys.argv)
    # Apply a New World Themed stylesheet
    # Font suggestion: For a more thematic feel, you could try fonts like "Cinzel", "Trajan Pro",
    # or a readable serif like "Georgia". Ensure the font is installed on the user's system.
    # For now, we'll stick to common sans-serif fonts for broad compatibility and UI clarity.
    app.setStyleSheet("""
        QWidget {
            background-color: #282c34; /* Dark bluish-grey */
            color: #abb2bf; /* Light grey text */
            font-family: "Segoe UI", "Helvetica Neue", sans-serif; /* Common sans-serif fonts */
            font-size: 10pt;
        }

        QMainWindow {
            background-color: #282c34; /* Consistent with QWidget */
        }

        QLabel {
            color: #abb2bf; /* Consistent with QWidget */
            background-color: transparent; /* Ensure labels don't have their own background unless specified */
        }

        QPushButton {
            background-color: #4682B4; /* SteelBlue */
            color: #ffffff; /* White text for contrast */
            border: 1px solid #3671a3; /* Darker blue border */
            padding: 5px 10px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #5a9bd4; /* Lighter SteelBlue */
        }

        QPushButton:pressed {
            background-color: #3671a3; /* Darker SteelBlue */
        }

        QPushButton:disabled {
            background-color: #3a3f4b; /* Desaturated dark blue-grey */
            color: #7f848e; /* Desaturated text */
            border-color: #30343d;
        }

        QTreeWidget {
            background-color: #21252b; /* Slightly darker than main bg */
            color: #abb2bf; /* Light grey text */
            border: 1px solid #3c4049; /* Border matching the theme */
            selection-background-color: #d4af37; /* Metallic Gold for selection */
            selection-color: #1c1f24; /* Dark text on gold selection for contrast */
        }

        QHeaderView::section {
            background-color: #3c4049; /* Medium dark grey-blue */
            color: #e0e6f1; /* Light blueish-white text */
            padding: 4px;
            border: 1px solid #4a505a; /* Header border */
            border-bottom: none;
        }

        QSlider::groove:horizontal {
            border: 1px solid #3c4049; /* Thematic border */
            height: 8px; /* the groove expands to the size of the slider */
            background: #21252b; /* Background matching tree */
            margin: 2px 0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #d4af37; /* Metallic Gold handle */
            border: 1px solid #b89028; /* Darker Gold border for handle */
            width: 18px;
            margin: -5px 0; /* handle is placed vertically centered to the groove */
            border-radius: 9px;
        }

        QDoubleSpinBox {
            background-color: #21252b; /* Consistent with tree/slider groove */
            color: #abb2bf; /* Light grey text */
            border: 1px solid #3c4049; /* Thematic border */
            padding: 2px;
            border-radius: 3px;
        }

        QStatusBar {
            background-color: #1c1f24; /* Very dark background for status bar */
            color: #9da5b3; /* Muted text for status bar */
            border-top: 1px solid #323840; /* Subtle top border */
        }

        QStatusBar::item {
            border: none; /* Remove border between status bar items */
        }

        QToolTip {
            background-color: #323840; /* Dark grey-blue, similar to header */
            color: #c8cdd4;           /* Light grey text */
            border: 1px solid #4a505a; /* Consistent border */
            padding: 3px;
            /* opacity: 230; */ /* Opacity can be tricky with QToolTip, often ignored */
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Starting NeWWorld-Config-Manager...")
    run_app()