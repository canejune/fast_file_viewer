# FastFileViewer :: ui/search_results_window.py
# Window to display only regex search results.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QTextBrowser
from PySide6.QtCore import Qt

class SearchResultsWindow(QWidget): # Could also be a QDialog
    """
    Displays only the lines that match the currently active
    search regex patterns.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Results")
        self.setWindowFlags(Qt.WindowType.Tool) # Example: make it a tool window

        layout = QVBoxLayout(self)
        self.results_display = QTextBrowser() # Or QListWidget, or custom view
        self.results_display.setReadOnly(True)
        layout.addWidget(self.results_display)
        self.setLayout(layout)

    def display_results(self, matching_lines_with_context):
        """
        Clears previous results and displays new matching lines.
        `matching_lines_with_context` could be a list of strings or more complex objects.
        """
        self.results_display.clear()
        for line_info in matching_lines_with_context:
            self.results_display.append(str(line_info)) # Adjust as needed