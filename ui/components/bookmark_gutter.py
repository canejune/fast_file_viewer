# FastFileViewer :: ui/components/bookmark_gutter.py
# Custom widget for the bookmark gutter.

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtCore import Qt, QSize

# from utils.constants import BOOKMARK_ICON_PATH # Example

class BookmarkGutter(QWidget):
    """
    A widget for displaying bookmark icons next to lines.
    """
    def __init__(self, editor_view):
        super().__init__(editor_view)
        self.editor_view = editor_view
        # self.bookmark_icon = QPixmap(BOOKMARK_ICON_PATH) # Load icon

    def sizeHint(self):
        return QSize(20, 0) # Example fixed width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(Qt.GlobalColor.lightGray).lighter(130))
        # Logic to draw bookmark icons for visible bookmarked lines