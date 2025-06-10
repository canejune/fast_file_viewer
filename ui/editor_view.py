# FastFileViewer :: ui/editor_view.py
# Central text display area, line numbers, gutters.

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QAbstractScrollArea
from PySide6.QtGui import QFont, QPainter, QColor
from PySide6.QtCore import Qt, QRect, QSize

from .components.line_number_area import LineNumberArea
# from .components.bookmark_gutter import BookmarkGutter
# from .components.timestamp_gutter import TimestampGutter

# Forward declaration for type hinting if MinimapView is in the same module or imported later
# class MinimapView: pass

class EditorView(QWidget): # Changed from QPlainTextEdit
    """
    Displays the file content with line numbers and other gutter information.
    This widget now contains a QPlainTextEdit and a LineNumberArea.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap) # Important for minimap sync
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
        self.text_edit.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)
        # self.text_edit.cursorPositionChanged.connect(self.line_number_area.update) # For current line highlight in gutter

        self.update_line_number_area_width() # Initial width calculation
        self.minimap_view_ref = None # Reference to the minimap

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

    def link_minimap(self, minimap_view): # minimap_view is of type MinimapView
        """Links this editor view to a minimap view."""
        self.minimap_view_ref = minimap_view
        if self.minimap_view_ref:
            self.minimap_view_ref.scroll_request.connect(self.scroll_to_percentage)
            # Initial update of minimap's visible rect
            self._on_scroll_changed() 



    # --- Methods to forward to self.text_edit ---
    def append_lines(self, lines: list):
        """Appends a list of lines to the editor."""
        self.text_edit.appendPlainText("\n".join(lines))

    def set_text_content(self, lines_list: list):
        """Sets the entire text content of the editor from a list of lines."""
        self.text_edit.clear()
        self.text_edit.setPlainText("\n".join(lines_list))
        # After setting content, update minimap's visible area
        self._on_scroll_changed()

    def set_view_font(self, font_family: str, font_size: int):
        """Sets the font for the editor view."""
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        # Font change might affect line number area width and appearance
        self.update_line_number_area_width() # Recalculate width
        self.line_number_area.update()       # Repaint gutter
        if self.minimap_view_ref: # Update minimap if font changes
            self.minimap_view_ref.setFont(font) # Or a scaled version
            self._on_scroll_changed()

    def clear(self):
        """Clears the text editor content."""
        self.text_edit.clear()
        if self.minimap_view_ref:
            self.minimap_view_ref.clear_content()

    def _on_scroll_changed(self, value=None): # value can be ignored if not directly used
        """Called when the editor's vertical scrollbar changes."""
        if self.minimap_view_ref:
            self.minimap_view_ref.update_visible_rect(self.text_edit.verticalScrollBar())

    def scroll_to_percentage(self, percentage: float):
        """Scrolls the editor view to a given percentage (0.0 to 1.0)."""
        scrollbar = self.text_edit.verticalScrollBar()
        scroll_range = scrollbar.maximum() - scrollbar.minimum()
        target_value = int(scrollbar.minimum() + scroll_range * percentage)
        scrollbar.setValue(target_value)

    # Add other QPlainTextEdit methods you need to expose as needed