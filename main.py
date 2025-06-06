# FastFileViewer :: main.py
# Application entry point.
# Initializes the Qt application, creates the main window instance, and starts the Qt event loop.

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow # Assuming ui.main_window will be created

def main():
    """Main function to run the FastFileViewer application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    # print("FastFileViewer application started (placeholder).")

if __name__ == "__main__":
    main()
