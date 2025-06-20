# FastFileViewer :: ui/search_results_window.py
# Window to display only regex search results.
from PySide6.QtGui import QColor, QPainter, QFont, QFontMetrics
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, # Changed QLabel to QTextEdit for text_label
                               QScrollArea, QFrame, QHBoxLayout, QApplication)
from PySide6.QtCore import Qt
LINE_NUMBER_GUTTER_WIDTH = 50 # Width for the line number gutter in search results

class SearchResultsWindow(QWidget): # Could also be a QDialog
    """
    Displays only the lines that match the currently active
    search regex patterns.
    """
    def __init__(self, parent=None):
        super().__init__(parent) # Pass parent to ensure proper window management
        self.setWindowTitle("Search Results")
        self.setWindowFlags(Qt.WindowType.Tool) # Example: make it a tool window
        self.resize(600, 400) # Set a default size

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.results_widget = QWidget() # This widget will contain all result items
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0,0,0,0)
        self.results_layout.setSpacing(0)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Items stack from top

        self.scroll_area.setWidget(self.results_widget)
        self.main_layout.addWidget(self.scroll_area)

        # Store a reference to the main window's editor_view if needed for jumping to lines
        self.editor_view_ref = None
        if parent and hasattr(parent, 'editor_view'):
            self.editor_view_ref = parent.editor_view

        self.current_font = QApplication.font() # Default application font
        if self.editor_view_ref: # Try to use editor's font
            self.current_font = self.editor_view_ref.text_edit.font()


    def display_results(self, results: list):
        """
        Clears previous results and displays new matching lines.
        `results` is a list of tuples: (line_number_0_indexed, line_text, type_str, fg_color, bg_color)
        """
        # Clear previous results
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not results:
            no_results_label = QLabel("No matches or bookmarks found.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(no_results_label)
            return

        for line_number, line_text, result_type, fg_color, bg_color in results:
            item_widget = SearchResultItem(line_number, line_text, result_type,
                                           fg_color, bg_color, self.current_font,
                                           self.editor_view_ref)
            self.results_layout.addWidget(item_widget)


class SearchResultItem(QFrame):
    """Custom widget to display a single search result item with line number and styling."""
    def __init__(self, line_number_0_indexed: int, line_text: str, result_type: str,
                 fg_color: QColor, bg_color: QColor, font: QFont, editor_view_ref, parent=None):
        super().__init__(parent)
        self.line_number = line_number_0_indexed
        self.line_text_content = line_text
        self.result_type_info = result_type
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.editor_view_ref = editor_view_ref

        self.setObjectName("SearchResultItem") # For specific QFrame styling
        self.setFrameShape(QFrame.Shape.NoFrame) # No border for the item itself
        # self.setFrameShadow(QFrame.Shadow.Plain)
        # self.setLineWidth(0)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        # Line Number Gutter
        self.line_no_label = QLabel(f"{self.line_number + 1}")
        self.line_no_label.setFixedWidth(LINE_NUMBER_GUTTER_WIDTH)
        self.line_no_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.line_no_label.setContentsMargins(0, 2, 5, 2) # top, bottom, right padding
        self.line_no_label.setFont(font)
        
        # Line Text
        self.text_label = QTextEdit(self.line_text_content) # Changed from QLabel to QTextEdit
        self.text_label.setReadOnly(True) # Make it non-editable
        self.text_label.setFont(font)
        # QTextEdit handles its own alignment and margins, so direct alignment might not be needed here.
        # self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.text_label.setContentsMargins(5, 2, 5, 2) # Still useful for padding
        self.text_label.setFont(font)
        self.text_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Hide vertical scrollbar
        self.text_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) # Show horizontal if needed
        self.text_label.setFixedHeight(QFontMetrics(font).height() + 4) # Approximate height for a single line + padding

        layout.addWidget(self.line_no_label)
        layout.addWidget(self.text_label, 1) # Text label takes remaining space

        # Determine if this item primarily represents a bookmark for styling
        is_bookmark_type = "Bookmark" in self.result_type_info # Does this line have a bookmark?
        is_regex_type = any(rt.startswith("Regex:") for rt in self.result_type_info.split(", ")) # Does this line have regex match?

        item_bg_color_name = None
        gutter_bg_color_name = None
        text_label_fg_color_name = None
        gutter_label_fg_color_name = "grey" # Default gutter text color

        # MainWindow ensures that self.bg_color is the regex background if both types are present.
        # If only bookmark, self.bg_color is the bookmark color.
        if is_regex_type: # If it's a regex match (possibly also a bookmark)
            if self.bg_color and self.bg_color.isValid():
                item_bg_color_name = self.bg_color.name() # Regex bg for the whole item
        elif is_bookmark_type: # Only a bookmark, no regex match on this line from higher priority patterns
            if self.bg_color and self.bg_color.isValid(): # This bg_color is the bookmark color
                gutter_bg_color_name = self.bg_color.name()
            # item_bg_color_name remains None (default)

        if self.fg_color and self.fg_color.isValid():
            text_label_fg_color_name = self.fg_color.name()
            if self.fg_color.alpha() > 0 : gutter_label_fg_color_name = self.fg_color.name()

        # Apply styles
        if item_bg_color_name:
            # Set background for the QFrame
            self.setStyleSheet(f"QFrame#SearchResultItem {{ background-color: {item_bg_color_name}; border: none; }}")
            # Ensure QTextEdit background is transparent and has correct text color
            text_color_for_label = text_label_fg_color_name if text_label_fg_color_name else 'black'
            self.text_label.setStyleSheet(f"QTextEdit {{ background-color: transparent; border: none; color: {text_color_for_label}; }}")
        else: # No item background color (e.g. bookmark only)
            # Ensure default background for QFrame and set text color for label
            self.setStyleSheet(f"QFrame#SearchResultItem {{ background-color: transparent; border: none; }}") # Default transparent
            text_color_for_label = text_label_fg_color_name if text_label_fg_color_name else 'black'
            self.text_label.setStyleSheet(f"QTextEdit {{ background-color: transparent; border: none; color: {text_color_for_label}; }}")

        gutter_styles = []
        if gutter_bg_color_name:
            gutter_styles.append(f"background-color: {gutter_bg_color_name};")
        if gutter_label_fg_color_name:
            gutter_styles.append(f"color: {gutter_label_fg_color_name};")
        if gutter_styles:
            self.line_no_label.setStyleSheet(f"QLabel {{ {' '.join(gutter_styles)} }}")
        else: # Ensure default gutter text color if no specific style
            self.line_no_label.setStyleSheet(f"QLabel {{ color: grey; background-color: transparent; }}")


    def mousePressEvent(self, event):
        # On any click, try to scroll the main editor to this line
        if event.button() == Qt.MouseButton.LeftButton and self.editor_view_ref:
            self.editor_view_ref.scroll_to_line(self.line_number)
        # QTextEdit handles its own cursor and selection on press, so call super for that.
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handles double-click on a result item to jump to the line in the main editor."""
        # The mousePressEvent already handles scrolling. Double-click might have additional actions in the future.
        # For now, the press event's scroll is sufficient.
        super().mouseDoubleClickEvent(event)