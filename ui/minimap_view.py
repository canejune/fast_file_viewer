# FastFileViewer :: ui/minimap_view.py
# Document overview/minimap component.

from PySide6.QtWidgets import QWidget, QAbstractScrollArea
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics, QMouseEvent
from PySide6.QtCore import Qt, Signal, QRectF

# A simple representation of a line for the minimap
class MinimapLine:
    def __init__(self, text):
        self.text = text # Store original text for potential advanced rendering

class MinimapView(QWidget):
    """
    Displays a scrollable document overview (minimap).
    Renders a scaled-down version of the document, highlighting
    bookmarked lines and regex matches. Allows navigation.
    """
    # Signal to indicate user wants to scroll to a certain percentage of the document
    scroll_request = Signal(float) # float is percentage from 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(80) # Adjust as needed
        self.setMaximumWidth(200)
        self._document_lines = [] # Stores MinimapLine objects
        self._visible_rect_fraction = QRectF(0, 0, 1, 0.1) # x, y, w, h as fractions of minimap
        self._line_height = 2 # Height of each line in the minimap in pixels
        self._text_color = QColor(Qt.GlobalColor.gray)
        self._background_color = QColor(Qt.GlobalColor.lightGray).lighter(110)
        self._visible_area_color = QColor(Qt.GlobalColor.darkGray).lighter(50)
        self._visible_area_color.setAlpha(100) # Semi-transparent

        self.editor_scroll_bar = None # To get scroll range and position

        # self.bookmark_manager = None
        # self.regex_engine = None
        self.setFont(QFont("Monospace", 1)) # Tiny font for minimap representation

    def set_document_content(self, lines: list):
        """Receives the full document content (list of strings)."""
        self._document_lines = [MinimapLine(line) for line in lines]
        self.update() # Trigger repaint

    def update_visible_rect(self, editor_scroll_bar: QAbstractScrollArea):
        """
        Updates the position and size of the rectangle indicating the
        editor's visible area on the minimap.
        """
        if not self._document_lines or not editor_scroll_bar:
            return

        self.editor_scroll_bar = editor_scroll_bar
        scroll_value = editor_scroll_bar.value()
        scroll_min = editor_scroll_bar.minimum()
        scroll_max = editor_scroll_bar.maximum()
        page_step = editor_scroll_bar.pageStep()

        # total_range includes the page_step itself, representing the full scrollable content height
        total_range = scroll_max - scroll_min + page_step

        if total_range <= 0 or page_step <= 0: # Avoid division by zero or invalid states
            self._visible_rect_fraction.setY(0)
            self._visible_rect_fraction.setHeight(1.0)
        else:
            # Calculate the start of the visible area (0.0 to 1.0)
            # Ensure scroll_value is within bounds for calculation
            current_pos_in_range = max(0, scroll_value - scroll_min)
            visible_start_ratio = current_pos_in_range / total_range
            # Calculate the height of the visible area (0.0 to 1.0)
            visible_height_ratio = page_step / total_range
            self._visible_rect_fraction.setY(min(visible_start_ratio, 1.0 - visible_height_ratio)) # Ensure it doesn't go out of bounds
            self._visible_rect_fraction.setHeight(visible_height_ratio)
        
        self.update()

    def paintEvent(self, event):
        """
        Renders the minimap.
        This will involve drawing scaled lines, bookmarks, and highlights.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._background_color)

        if not self._document_lines:
            painter.end()
            return

        # Simple rendering: draw a small rectangle for each line
        # More advanced: draw tiny text or representations of text structure
        painter.setPen(self._text_color)
        
        total_lines = len(self._document_lines)
        # Calculate how many lines can fit vs how many there are
        # This determines the effective line height for drawing if scaling is needed
        # For now, use fixed self._line_height and let it scroll if too many lines

        y_offset = 0
        for i, m_line in enumerate(self._document_lines):
            # A very basic representation of a line
            # For a VSCode like minimap, you'd analyze m_line.text
            # and draw a more representative glyph or scaled text.
            # Here, we just draw a small horizontal line.
            if m_line.text.strip(): # Draw something if line is not empty
                 painter.drawLine(2, y_offset + 1, self.width() - 4, y_offset + 1)
            y_offset += self._line_height
            if y_offset > self.height(): # Stop if we've drawn past the bottom
                break
        
        # Draw the rectangle for the visible area
        if self.editor_scroll_bar: # Only draw if we have scrollbar info
            rect_y = self._visible_rect_fraction.y() * self.height()
            rect_height = self._visible_rect_fraction.height() * self.height()
            painter.fillRect(QRectF(0, rect_y, self.width(), rect_height), self._visible_area_color)

        painter.end()

    def _y_to_percentage(self, y_pos: int) -> float:
        """Converts a Y coordinate on the minimap to a document percentage."""
        if self.height() == 0:
            return 0.0
        return max(0.0, min(1.0, y_pos / self.height()))

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            percentage = self._y_to_percentage(event.position().y())
            self.scroll_request.emit(percentage)
            self._is_dragging = True # For potential drag scrolling

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton and getattr(self, '_is_dragging', False):
            percentage = self._y_to_percentage(event.position().y())
            self.scroll_request.emit(percentage)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False

    def clear_content(self):
        self._document_lines = []
        self.update()