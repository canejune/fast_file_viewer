# FastFileViewer :: core/bookmark_manager.py
# Manages bookmarked line numbers.

from PySide6.QtGui import QColor # Import QColor
from PySide6.QtCore import QObject, Signal

class BookmarkManager(QObject):
    """
    Manages a set of bookmarked line numbers (0-indexed).
    Emits a signal when the set of bookmarks changes.
    """
    bookmarks_changed = Signal(set)  # Emits the new set of bookmarked line numbers
    bookmark_color_changed = Signal(QColor) # Emits when the global bookmark color changes

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self._settings_manager = settings_manager
        self._current_filepath = None
        self._bookmarked_lines = set() # Bookmarks for the _current_filepath

    def set_current_file(self, filepath: str | None):
        """Sets the current file and loads its bookmarks."""
        self._current_filepath = filepath
        if self._current_filepath:
            self._bookmarked_lines = self._settings_manager.load_bookmarks(self._current_filepath)
        else:
            self._bookmarked_lines = set()
        self.bookmarks_changed.emit(self._bookmarked_lines.copy()) # Notify UI about bookmark changes for the new file

    def toggle_bookmark(self, line_number: int):
        """Adds or removes a bookmark for the given line number."""
        if not self._current_filepath: return # No file loaded
        if line_number in self._bookmarked_lines:
            self._bookmarked_lines.remove(line_number)
        else:
            self._bookmarked_lines.add(line_number)
        self._save_and_emit_change()

    def add_bookmark(self, line_number: int):
        """Adds a bookmark if it doesn't exist."""
        if not self._current_filepath: return
        if line_number not in self._bookmarked_lines:
            self._bookmarked_lines.add(line_number)
            self._save_and_emit_change()

    def remove_bookmark(self, line_number: int):
        """Removes a bookmark if it exists."""
        if not self._current_filepath: return
        if line_number in self._bookmarked_lines:
            self._bookmarked_lines.remove(line_number)
            self._save_and_emit_change()

    def is_bookmarked(self, line_number: int) -> bool:
        """Checks if a line is bookmarked."""
        # This check is against the currently loaded set for _current_filepath
        return line_number in self._bookmarked_lines

    def get_all_bookmarks(self) -> set:
        """Returns a copy of the set of all bookmarked line numbers."""
        return self._bookmarked_lines.copy()

    def clear_bookmarks_for_current_file(self):
        """Clears all bookmarks for the currently active file."""
        if not self._current_filepath: return
        if self._bookmarked_lines: # Only save and emit if there were bookmarks to clear
            self._bookmarked_lines.clear()
            self._save_and_emit_change()

    def _save_and_emit_change(self):
        if self._current_filepath:
            self._settings_manager.save_bookmarks(self._current_filepath, self._bookmarked_lines)
            self.bookmarks_changed.emit(self._bookmarked_lines.copy())

    def get_bookmark_color(self) -> QColor:
        return self._settings_manager.get_bookmark_color()

    def set_bookmark_color(self, color: QColor):
        self._settings_manager.set_bookmark_color(color)
        self.bookmark_color_changed.emit(color)