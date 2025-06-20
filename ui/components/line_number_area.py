# FastFileViewer :: ui/components/line_number_area.py
# Custom widget for line numbers.

from PySide6.QtWidgets import QWidget, QPlainTextEdit # Import QPlainTextEdit for type hinting
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QFont, QMouseEvent
from PySide6.QtCore import Qt, QSize, QRect # Import QRect

class LineNumberArea(QWidget):
    """
    A widget specifically for displaying line numbers adjacent
    to a text editor component (like QPlainTextEdit).
    """
    def __init__(self, editor: QPlainTextEdit): # editor is the QPlainTextEdit
        super().__init__(editor.parent()) # Parent is EditorView (QWidget)
        self.text_editor = editor # Store the QPlainTextEdit instance
        # Ensure the document's default font matches the editor's view font
        # This helps in consistent metric calculations if not all blocks have explicit formatting.
        self.text_editor.document().setDefaultFont(editor.font())
        self.bookmark_manager = None
        # self.bookmark_indicator_text = "●" # Or use an icon/image

    def sizeHint(self) -> QSize:
        """Returns the preferred size for the line number area."""
        # Calculate width based on the number of digits in the highest line number
        count = self.text_editor.blockCount()
        digits = len(str(count)) if count > 0 else 1
        # Ensure a minimum width, e.g., for "99 " or "999"
        if digits < 3: 
            digits = 3
        
        # Calculate space: (width of '9' * number of digits) + left padding + right padding
        # Using fontMetrics of the text_editor for accurate width calculation.
        # Add a bit of padding on both sides (e.g., 5px each).
        padding = 10 
        space = self.text_editor.fontMetrics().horizontalAdvance('9') * digits + padding
        return QSize(space, 0) # Height is managed by the layout

    def set_bookmark_manager(self, bookmark_manager):
        self.bookmark_manager = bookmark_manager
        if self.bookmark_manager:
            # Connect to color changes if the manager emits such a signal
            if hasattr(self.bookmark_manager, 'bookmark_color_changed'):
                self.bookmark_manager.bookmark_color_changed.connect(self.update)
            self.update() # Repaint if bookmarks are now available

    def paintEvent(self, event: QPaintEvent):
        """Paints the line numbers."""
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(Qt.GlobalColor.lightGray).lighter(110)) # Background color

        block = self.text_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        # Top y-coordinate of the first visible block in the text_editor's viewport
        top = self.text_editor.blockBoundingGeometry(block).translated(self.text_editor.contentOffset()).top()
        bottom = top + self.text_editor.viewport().height() # Bottom of the viewport

        painter.setFont(self.text_editor.font()) # Use editor's font
        painter.setPen(QColor(Qt.GlobalColor.darkGray))    # Line number color

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # Draw bookmark indicator if line is bookmarked
                if self.bookmark_manager and self.bookmark_manager.is_bookmarked(block_number):
                    # Fill the background for the bookmarked line number
                    # Adjust rect to not overwrite line numbers or to be a specific mark
                    bookmark_rect = QRect(0, int(top), self.width(), self.text_editor.fontMetrics().height())
                    current_bookmark_color = self.bookmark_manager.get_bookmark_color()
                    painter.fillRect(bookmark_rect, current_bookmark_color)
                    # Optionally, draw a symbol like a circle or use an icon
                    # painter.setPen(Qt.GlobalColor.black) # Color for the bookmark symbol
                    # painter.drawText(2, int(top), self.width() - 7, self.text_editor.fontMetrics().height(), Qt.AlignmentFlag.AlignLeft, self.bookmark_indicator_text)

                number = str(block_number + 1)
                painter.setPen(QColor(Qt.GlobalColor.darkGray)) # Reset pen for line number
                painter.drawText(0, int(top), self.width() - 5, self.text_editor.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = self.text_editor.blockBoundingGeometry(block).translated(self.text_editor.contentOffset()).top()
            block_number += 1
            if not block.isValid(): # Break if no more blocks
                break
        painter.end() # Explicitly end painting

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.bookmark_manager:
            # Determine the block (line number) clicked using the editor's cursorForPosition
            # This is a more robust way to map a widget coordinate to a block number
            # as it accounts for scrolling and block geometry.
            pos_in_editor_viewport = self.mapToParent(event.position().toPoint()) # Map click position to EditorView coordinates
            cursor = self.text_editor.cursorForPosition(pos_in_editor_viewport)
            clicked_line_number = cursor.blockNumber()

            self.bookmark_manager.toggle_bookmark(clicked_line_number)
            # self.update() # The bookmarks_changed signal from manager should trigger this via EditorView
        super().mousePressEvent(event)