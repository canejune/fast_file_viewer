# FastFileViewer :: ui/editor_view.py
# Central text display area, line numbers, gutters.

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QSize

from .components.line_number_area import LineNumberArea
# from .components.bookmark_gutter import BookmarkGutter
# from .components.timestamp_gutter import TimestampGutter

class EditorView(QWidget): # Changed from QPlainTextEdit
    """
    Displays the file content with line numbers and other gutter information.
    This widget now contains a QPlainTextEdit and a LineNumberArea.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 10)) # Default font

        self.line_number_area = LineNumberArea(self.text_edit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Remove margins
        layout.setSpacing(0) # Remove spacing between widgets
        layout.addWidget(self.line_number_area)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # Connect signals for scrollbar changes to update gutters if they exist
        self.text_edit.blockCountChanged.connect(self.update_line_number_area_width)
        self.text_edit.updateRequest.connect(self.update_line_number_area)
        # self.text_edit.cursorPositionChanged.connect(self.line_number_area.update) # For current line highlight in gutter

        self.update_line_number_area_width() # Initial width calculation

    def update_line_number_area_width(self, _=None): # Parameter can be ignored
        """Updates the width of the line number area."""
        self.line_number_area.updateGeometry() # Triggers sizeHint recalculation and layout update

    def update_line_number_area(self, rect: QRect, dy: int):
        """Scrolls the line number area or updates its content."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            # rect contains the area in the text_edit that needs repaint.
            # We need to update a corresponding area in the line_number_area.
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        # If the viewport itself is part of the update rect (e.g. full repaint)
        if rect.contains(self.text_edit.viewport().rect()):
            self.update_line_number_area_width()


    # --- Methods to forward to self.text_edit ---
    def append_lines(self, lines: list):
        """Appends a list of lines to the editor."""
        self.text_edit.appendPlainText("\n".join(lines))

    def set_text_content(self, lines_list: list):
        """Sets the entire text content of the editor from a list of lines."""
        self.text_edit.clear()
        self.text_edit.setPlainText("\n".join(lines_list))

    def set_view_font(self, font_family: str, font_size: int):
        """Sets the font for the editor view."""
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        # Font change might affect line number area width and appearance
        self.update_line_number_area_width() # Recalculate width
        self.line_number_area.update()       # Repaint gutter

    def clear(self):
        """Clears the text editor content."""
        self.text_edit.clear()

    # Add other QPlainTextEdit methods you need to expose as needed