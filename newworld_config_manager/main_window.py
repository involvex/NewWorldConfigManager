import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeWWorld-Config-Manager")
        self.setGeometry(100, 100, 600, 400)  # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.label = QLabel("Welcome to NeWWorld Config Manager!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.load_button = QPushButton("Load Config (Not Implemented)")
        layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Config (Not Implemented)")
        layout.addWidget(self.save_button)

        self.central_widget.setLayout(layout)