# FastFileViewer :: core/settings_manager.py
# Manages application settings and user preferences.

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

    # Add more methods for font, window size, regex patterns, bookmarks etc.
    # def save_bookmarks(self, bookmarks_set):
    #     self.set_setting("bookmarks", list(bookmarks_set))

    # def load_bookmarks(self):
    #     return set(self.get_setting("bookmarks", []))