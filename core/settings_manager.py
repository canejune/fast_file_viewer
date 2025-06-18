# FastFileViewer :: core/settings_manager.py
# Manages application settings and user preferences.
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt # Added import for Qt
from PySide6.QtCore import QObject, QSettings
from utils.constants import MAX_RECENT_FILES

class SettingsManager(QObject):
    """
    Handles persistence of application settings.
    """
    ORGANIZATION_NAME = "MyCompany" # Replace with your organization name
    APPLICATION_NAME = "FastFileViewer"
    DEFAULT_FONT_FAMILY = "Courier New"
    DEFAULT_FONT_SIZE = 10


    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings(QSettings.Format.IniFormat,
                                   QSettings.Scope.UserScope,
                                   self.ORGANIZATION_NAME,
                                   self.APPLICATION_NAME)

    def get_setting(self, key, default_value=None):
        """Retrieves a setting value."""
        return self.settings.value(key, default_value)

    def set_setting(self, key, value):
        """Saves a setting value."""
        self.settings.setValue(key, value)

    # Example specific settings methods
    def get_recent_files(self):
        """Gets the list of recent files."""
        return self.get_setting("recentFiles", [])

    def add_recent_file(self, filepath):
        """Adds a file to the recent files list."""
        recent_files = self.get_recent_files()
        if filepath in recent_files:
            recent_files.remove(filepath)
        recent_files.insert(0, filepath)
        self.set_setting("recentFiles", recent_files[:MAX_RECENT_FILES])

    def clear_recent_files(self):
        """Clears the list of recent files from settings."""
        self.set_setting("recentFiles", [])
        print("[SettingsManager] Cleared recent files.")

    def get_editor_font_family(self):
        """Gets the editor font family."""
        return self.get_setting("editor/fontFamily", self.DEFAULT_FONT_FAMILY)

    def set_editor_font_family(self, font_family: str):
        """Sets the editor font family."""
        self.set_setting("editor/fontFamily", font_family)

    def get_editor_font_size(self):
        """Gets the editor font size."""
        return int(self.get_setting("editor/fontSize", self.DEFAULT_FONT_SIZE))

    def set_editor_font_size(self, font_size: int):
        """Sets the editor font size."""
        self.set_setting("editor/fontSize", font_size)

    def save_regex_patterns(self, patterns_list: list):
        """
        Saves regex patterns to settings.
        Each pattern in patterns_list is a dict:
        {"id": str, "pattern_str": str, "fg_color": QColor, "bg_color": QColor, "is_active": bool}
        QColor is saved as its name (e.g., "#RRGGBB").
        """
        serializable_patterns = []
        for p in patterns_list:
            serializable_patterns.append({
                "id": p["id"],
                "pattern_str": p["pattern_str"],
                "fg_color_name": p.get("fg_color", QColor(Qt.GlobalColor.black)).name(), # Default to black if missing
                "bg_color_name": p.get("bg_color", QColor(Qt.GlobalColor.yellow)).name(), # Default to yellow if missing
                "is_active": p["is_active"]
            })
        self.set_setting("regexPatterns", serializable_patterns)

    def load_regex_patterns(self) -> list:
        """
        Loads regex patterns from settings.
        Returns a list of pattern dicts, converting color names back to QColor.
        """
        loaded_patterns_data = self.get_setting("regexPatterns", [])
        patterns = []
        for p_data in loaded_patterns_data:
            patterns.append({
                "id": p_data["id"],
                "pattern_str": p_data["pattern_str"],
                "fg_color": QColor(p_data.get("fg_color_name", Qt.GlobalColor.black.name)),
                "bg_color": QColor(p_data.get("bg_color_name", Qt.GlobalColor.yellow.name)),
                "is_active": p_data["is_active"]
            })
        return patterns

    # def load_bookmarks(self):
    #     return set(self.get_setting("bookmarks", []))