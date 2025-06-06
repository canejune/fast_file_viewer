# FastFileViewer :: ui/components/timestamp_gutter.py
# Custom widget for the timestamp gutter.

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QSize

class TimestampGutter(QWidget):
    """
    A widget for displaying parsed timestamps next to lines.
    """
    def __init__(self, editor_view):
        super().__init__(editor_view)
        self.editor_view = editor_view

    def sizeHint(self):
        return QSize(100, 0) # Example width, might need to be dynamic

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(Qt.GlobalColor.lightGray).lighter(140))
        # Logic to draw parsed timestamps for visible lines