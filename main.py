import sys
from PyQt6.QtWidgets import QApplication
from newworld_config_manager.main_window import MainWindow

def run_app():
    """Initializes and runs the PyQt6 application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    print("Starting NeWWorld-Config-Manager...")
    run_app()