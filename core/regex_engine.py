# FastFileViewer :: core/regex_engine.py
# Processes regular expressions, finds matches.

import re
from PySide6.QtCore import QObject, Signal

class RegexEngine(QObject):
    """
    Manages and applies regular expression patterns for searching and highlighting.
    """
    # Signal emitted when regex patterns or their properties change
    patterns_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # List of tuples: (pattern_string, compiled_regex, color, is_active)
        self._patterns = []

    def add_pattern(self, pattern_string, color, is_active=True):
        """
        Adds a new regex pattern.
        """
        try:
            compiled_regex = re.compile(pattern_string)
            self._patterns.append({"raw": pattern_string, "compiled": compiled_regex, "color": color, "active": is_active})
            self.patterns_changed.emit()
            return True
        except re.error as e:
            print(f"Invalid regex pattern '{pattern_string}': {e}")
            return False

    def remove_pattern(self, index):
        """Removes a pattern by its index."""
        if 0 <= index < len(self._patterns):
            del self._patterns[index]
            self.patterns_changed.emit()

    def get_active_patterns(self):
        """Returns a list of active compiled regex patterns and their colors."""
        return [(p["compiled"], p["color"]) for p in self._patterns if p["active"]]

    def find_matches(self, text_line):
        """
        Finds all matches for active patterns in a given line of text.
        Returns a list of (match_object, color) for highlighting.
        """
        matches_with_color = []
        for compiled_regex, color in self.get_active_patterns():
            for match in compiled_regex.finditer(text_line):
                matches_with_color.append((match, color))
        return matches_with_color

    def get_all_patterns_info(self):
        """Returns all patterns with their info (raw, color, active)."""
        return [{"raw": p["raw"], "color": p["color"], "active": p["active"]} for p in self._patterns]

    def set_pattern_active(self, index, active_status):
        """Sets the active status of a pattern by index."""
        if 0 <= index < len(self._patterns):
            self._patterns[index]["active"] = active_status
            self.patterns_changed.emit()