import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from newworld_config_manager.main_window import MainWindow

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, which works for both development (running as a script)
    and for a bundled executable created by PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores its path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # _MEIPASS is not set, so we are running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_stylesheet(path: str) -> str:
    """Loads a stylesheet from a file and returns it as a string."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Stylesheet not found at '{path}'. Using default styles.")
        return ""
    except Exception as e:
        print(f"Error loading stylesheet from '{path}': {e}")
        return ""

def run_app():
    """Initializes and runs the PyQt6 application."""
    app = QApplication(sys.argv)
    
    # Load the stylesheet from an external file for better maintainability.
    # Use the resource_path helper to find it correctly.
    stylesheet = load_stylesheet(resource_path('assets/stylesheet.qss'))
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()

    # Set the icon for the application window itself (taskbar, title bar)
    # Use the resource_path helper to find the icon correctly.
    window.setWindowIcon(QIcon(resource_path('assets/icon.ico')))

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Starting NeWWorld-Config-Manager...")
    run_app()