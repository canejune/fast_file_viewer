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

    def __init__(self, regex_engine, bookmark_manager, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(80) # Adjust as needed
        self.setMaximumWidth(200)
        self.bookmark_manager = bookmark_manager
        self._document_lines = [] # Stores MinimapLine objects
        self._visible_rect_fraction = QRectF(0, 0, 1, 0.1) # x, y, w, h as fractions of minimap
        self._line_height = 2 # Height of each line in the minimap in pixels
        self._default_line_indicator_color = QColor(Qt.GlobalColor.gray) # Color for non-empty lines without regex match
        self._minimap_background_color = QColor(Qt.GlobalColor.lightGray).lighter(110)
        self._visible_area_color = QColor(Qt.GlobalColor.darkGray).lighter(50)
        self._visible_area_color.setAlpha(100) # Semi-transparent
        # self._bookmark_minimap_color = QColor(Qt.GlobalColor.blue).lighter(120) # Will get from bookmark_manager

        self.editor_scroll_bar = None # To get scroll range and position
        self.regex_engine = regex_engine
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
        
        # If scroll_max is 0, it means content fits and no scrolling is needed.
        # In this case, the visible area is the entire document.
        if scroll_max == 0:
            self._visible_rect_fraction.setY(0)
            self._visible_rect_fraction.setHeight(1.0)
        else:
            # total_range includes the page_step itself, representing the full scrollable content height
            total_range = scroll_max - scroll_min + page_step
            if total_range <= 0 or page_step <= 0: # Should not happen if scroll_max > 0
                self._visible_rect_fraction.setY(0)
                self._visible_rect_fraction.setHeight(1.0)
                return # Avoid further calculation if state is invalid
            # Calculate the start of the visible area (0.0 to 1.0)
            current_pos_in_range = max(0, scroll_value - scroll_min)
            visible_start_ratio = current_pos_in_range / total_range
            visible_height_ratio = page_step / total_range
            self._visible_rect_fraction.setY(min(visible_start_ratio, 1.0 - visible_height_ratio)) # Ensure it doesn't go out of bounds
            self._visible_rect_fraction.setHeight(visible_height_ratio)
        
        self.update()

    def paintEvent(self, event):
        """
        Renders the minimap.
        This will involve drawing scaled lines, bookmarks, and highlights.
        """
        if not self.isVisible():
            return

        painter = QPainter(self)
        painter.fillRect(self.rect(), self._minimap_background_color)

        if not self._document_lines:
            painter.end()
            return

        active_patterns = self.regex_engine.get_active_patterns()
        total_lines = len(self._document_lines)

        y_offset = 0
        for i, m_line in enumerate(self._document_lines):
            line_text = m_line.text
            line_bg_color_to_draw = None

            is_bookmarked = self.bookmark_manager and self.bookmark_manager.is_bookmarked(i)

            if active_patterns and self.regex_engine:
                for compiled_regex, fg_c, bg_c in active_patterns:
                    if compiled_regex.search(line_text):
                        line_bg_color_to_draw = bg_c
                        break # First active regex pattern match determines background
            

            if line_bg_color_to_draw:
                painter.fillRect(QRectF(0, y_offset, self.width(), self._line_height), line_bg_color_to_draw)
            elif is_bookmarked and self.bookmark_manager: # If no regex match but bookmarked, draw bookmark color
                current_bookmark_color = self.bookmark_manager.get_bookmark_color()
                painter.fillRect(QRectF(0, y_offset, self.width(), self._line_height), current_bookmark_color)
            elif line_text.strip(): # If no regex match, draw default indicator for non-empty lines
                painter.setPen(self._default_line_indicator_color)
                # Draw a small horizontal line in the middle of the allocated line height
                indicator_y = y_offset + self._line_height / 2
                painter.drawLine(2, int(indicator_y), self.width() - 4, int(indicator_y))

            # Could also draw a specific mark for bookmarks on top of regex colors if needed
            # if is_bookmarked:
            #     painter.fillRect(QRectF(0, y_offset, 3, self._line_height), self._bookmark_minimap_color.darker(120))

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

    def update_styles(self):
        """Forces a repaint, typically called when regex patterns change."""
        # This is also connected to bookmark_manager.bookmarks_changed
        # and bookmark_manager.bookmark_color_changed (if implemented in BM and connected in MainWindow)
        self.update()