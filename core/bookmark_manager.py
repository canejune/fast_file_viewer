# FastFileViewer :: core/bookmark_manager.py
# Manages bookmark data (add, remove, retrieve, types).

from PySide6.QtCore import QObject, Signal

class BookmarkManager(QObject):
    """
    Manages bookmarks for lines in a file.
    """
    # Signal emitted when bookmarks change (e.g., list_of_bookmarked_line_numbers)
    bookmarks_changed = Signal(set)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bookmarks = set() # Stores line numbers (0-indexed) that are bookmarked

    def add_bookmark(self, line_number):
        """Adds a bookmark to the given line number."""
        if line_number not in self._bookmarks:
            self._bookmarks.add(line_number)
            self.bookmarks_changed.emit(self._bookmarks)

    def remove_bookmark(self, line_number):
        """Removes a bookmark from the given line number."""
        if line_number in self._bookmarks:
            self._bookmarks.remove(line_number)
            self.bookmarks_changed.emit(self._bookmarks)

    def toggle_bookmark(self, line_number):
        """Toggles a bookmark for the given line number."""
        if line_number in self._bookmarks:
            self.remove_bookmark(line_number)
        else:
            self.add_bookmark(line_number)

    def get_bookmarks(self):
        """Returns a set of all bookmarked line numbers."""
        return self._bookmarks.copy()

    def is_bookmarked(self, line_number):
        """Checks if a line is bookmarked."""
        return line_number in self._bookmarks

    def clear_bookmarks(self):
        """Removes all bookmarks."""
        self._bookmarks.clear()
        self.bookmarks_changed.emit(self._bookmarks)