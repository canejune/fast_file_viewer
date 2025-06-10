# FastFileViewer :: main.py
# Application entry point.
# Initializes the Qt application, creates the main window instance, and starts the Qt event loop.

import sys
import argparse
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow # Assuming ui.main_window will be created

def main():
    """Main function to run the FastFileViewer application."""
    parser = argparse.ArgumentParser(description="Fast File Viewer - A high-performance file viewer.")
    parser.add_argument('filepath', type=str, nargs='?', default=None,
                        help='Optional. The path to the file to open.')
    
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(initial_filepath=args.filepath)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
