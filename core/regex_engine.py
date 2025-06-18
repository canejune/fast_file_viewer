# FastFileViewer :: core/regex_engine.py
# Processes regular expressions, finds matches.

from PySide6.QtGui import QColor # For default colors
import uuid
import re
from PySide6.QtCore import QObject, Signal, Qt # Added Qt import

class RegexEngine(QObject):
    """
    Manages and applies regular expression patterns for searching and highlighting.
    """
    # Signal emitted when regex patterns or their properties change
    patterns_changed = Signal()

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        # List of dictionaries:
        # {"id": str, "pattern_str": str, "compiled": re.Pattern, "fg_color": QColor, "bg_color": QColor, "is_active": bool}
        self._patterns = []
        self._load_patterns_from_settings()

    def _load_patterns_from_settings(self):
        patterns_data = self.settings_manager.load_regex_patterns()
        self.set_patterns(patterns_data, save_to_settings=False) # Avoid re-saving immediately

    def get_patterns(self):
        """
        Returns a list of pattern data dictionaries suitable for the RegexDialog.
        Each dictionary contains: "id", "pattern_str", "fg_color", "bg_color", "is_active".
        Returns copies to prevent direct modification of internal state.
        """
        return [
            {"id": p["id"], "pattern_str": p["pattern_str"],
             "fg_color": p["fg_color"], "bg_color": p["bg_color"],
             "is_active": p["is_active"]}
            for p in self._patterns
        ]

    def set_patterns(self, patterns_data: list, save_to_settings: bool = True):
        """
        Sets the regex patterns from a list of dictionaries.
        Each dictionary in patterns_data should have: "id", "pattern_str", "fg_color", "bg_color", "is_active".
        This will recompile all patterns.
        """
        # print(f"RegexEngine.set_patterns called with: {patterns_data}")
        new_patterns = []
        for p_data in patterns_data:
            try:
                compiled_regex = re.compile(p_data["pattern_str"])
                new_patterns.append({
                    "id": p_data["id"],
                    "pattern_str": p_data["pattern_str"],
                    "compiled": compiled_regex,
                    "fg_color": p_data.get("fg_color", QColor(Qt.GlobalColor.black)),
                    "bg_color": p_data.get("bg_color", QColor(Qt.GlobalColor.yellow)),
                    "is_active": p_data["is_active"]
                })
            except re.error as e:
                print(f"Invalid regex pattern '{p_data['pattern_str']}' (ID: {p_data['id']}): {e}")
        self._patterns = new_patterns
        if save_to_settings:
            self.settings_manager.save_regex_patterns(self._patterns) # Save raw data with color objects
        self.patterns_changed.emit()

    def add_pattern(self, pattern_str: str, fg_color: QColor, bg_color: QColor,
                    is_active: bool = True, pattern_id: str = None):
        """
        Adds a new regex pattern.
        If pattern_id is None, a new UUID will be generated.
        """
        if pattern_id is None:
            pattern_id = str(uuid.uuid4())
        try:
            compiled_regex = re.compile(pattern_str)
            self._patterns.append({
                "id": pattern_id,
                "pattern_str": pattern_str,
                "compiled": compiled_regex,
                "fg_color": fg_color,
                "bg_color": bg_color,
                "is_active": is_active
            })
            self.settings_manager.save_regex_patterns(self._patterns)
            self.patterns_changed.emit()
            return True
        except re.error as e:
            print(f"Invalid regex pattern '{pattern_str}': {e}")
            return False

    def get_active_patterns(self):
        """Returns a list of (compiled_regex, fg_color, bg_color) for active patterns."""
        return [(p["compiled"], p["fg_color"], p["bg_color"]) for p in self._patterns if p["is_active"]]

    def find_matches(self, text_line):
        """
        Finds all matches for active patterns in a given line of text.
        Returns a list of (match_object, color) for highlighting.
        """
        matches_with_color = []
        for compiled_regex, fg_color, bg_color in self.get_active_patterns():
            for match in compiled_regex.finditer(text_line):
                matches_with_color.append((match, fg_color, bg_color)) # Now returns two colors
        return matches_with_color

    def remove_pattern(self, pattern_id: str):
        """Removes a pattern by its ID."""
        initial_len = len(self._patterns)
        self._patterns = [p for p in self._patterns if p["id"] != pattern_id]
        if len(self._patterns) < initial_len:
            self.settings_manager.save_regex_patterns(self._patterns)
            self.patterns_changed.emit()
            return True
        return False

    def set_pattern_active_status(self, pattern_id: str, is_active: bool):
        """Sets the active status of a pattern by ID."""
        for p in self._patterns:
            if p["id"] == pattern_id:
                if p["is_active"] != is_active:
                    p["is_active"] = is_active
                    self.settings_manager.save_regex_patterns(self._patterns)
                    self.patterns_changed.emit()
                return True
        return False