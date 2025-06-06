# FastFileViewer :: ui/components/line_number_area.py
# Custom widget for line numbers.

from PySide6.QtWidgets import QWidget, QPlainTextEdit
from PySide6.QtGui import QPainter, QColor, QPaintEvent, QFont
from PySide6.QtCore import Qt, QSize

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
                number = str(block_number + 1)
                painter.drawText(0, int(top), self.width() - 5, # x, y, width (-5 for right padding)
                                 self.text_editor.fontMetrics().height(), # height of a line
                                 Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = self.text_editor.blockBoundingGeometry(block).translated(self.text_editor.contentOffset()).top()
            block_number += 1
            if not block.isValid(): # Break if no more blocks
                break