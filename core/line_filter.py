# FastFileViewer :: core/line_filter.py
# Filters lines based on regex.

import re
from PySide6.QtCore import QObject, Signal

class LineFilter(QObject):
    """
    Manages regex patterns for filtering (hiding) lines.
    """
    # Signal emitted when filter patterns change
    filters_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # List of compiled regex patterns used for filtering
        self._filter_patterns = []

    def add_filter_pattern(self, pattern_string):
        """Adds a regex pattern for filtering lines."""
        try:
            compiled_regex = re.compile(pattern_string)
            self._filter_patterns.append(compiled_regex)
            self.filters_changed.emit()
        except re.error as e:
            print(f"Invalid filter regex pattern '{pattern_string}': {e}")

    def should_hide_line(self, text_line):
        """Checks if a line should be hidden based on the filter patterns."""
        for pattern in self._filter_patterns:
            if pattern.search(text_line):
                return True
        return False

    def clear_filters(self):
        """Removes all filter patterns."""
        self._filter_patterns.clear()
        self.filters_changed.emit()