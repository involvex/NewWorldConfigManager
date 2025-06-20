import sys
from PyQt6.QtWidgets import QApplication
from newworld_config_manager.main_window import MainWindow

def run_app():
    """Initializes and runs the PyQt6 application."""
    app = QApplication(sys.argv)

    # Apply a basic dark theme stylesheet
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b; /* Dark background */
            color: #cccccc; /* Light grey text */
            font-family: "Segoe UI", "Helvetica Neue", sans-serif; /* Common sans-serif fonts */
            font-size: 10pt;
        }

        QMainWindow {
            background-color: #2b2b2b;
        }

        QLabel {
            color: #cccccc;
        }

        QPushButton {
            background-color: #505050; /* Slightly lighter dark for buttons */
            color: #ffffff; /* White text */
            border: 1px solid #606060;
            padding: 5px 10px;
            border-radius: 3px;
        }

        QPushButton:hover {
            background-color: #606060;
        }

        QPushButton:pressed {
            background-color: #404040;
        }

        QPushButton:disabled {
            background-color: #3a3a3a;
            color: #808080;
            border-color: #4a4a4a;
        }

        QTreeWidget {
            background-color: #3c3c3c; /* Darker background for tree */
            color: #cccccc;
            border: 1px solid #505050;
            selection-background-color: #0078d7; /* Standard blue selection */
            selection-color: #ffffff;
        }

        QHeaderView::section {
            background-color: #4a4a4a; /* Dark header */
            color: #ffffff;
            padding: 4px;
            border: 1px solid #505050;
            border-bottom: none;
        }

        QSlider::groove:horizontal {
            border: 1px solid #505050;
            height: 8px; /* the groove expands to the size of the slider */
            background: #3c3c3c;
            margin: 2px 0;
            border-radius: 4px;
        }

        QSlider::handle:horizontal {
            background: #0078d7; /* Blue handle */
            border: 1px solid #0056b3;
            width: 18px;
            margin: -5px 0; /* handle is placed vertically centered to the groove */
            border-radius: 9px;
        }

        QDoubleSpinBox {
            background-color: #3c3c3c;
            color: #cccccc;
            border: 1px solid #505050;
            padding: 2px;
            border-radius: 3px;
        }

        QStatusBar {
            background-color: #4a4a4a;
            color: #cccccc;
            border-top: 1px solid #505050;
        }

        QStatusBar::item {
            border: none; /* Remove border between status bar items */
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Starting NeWWorld-Config-Manager...")
    run_app()