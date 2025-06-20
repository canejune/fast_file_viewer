# FastFileViewer :: ui/preferences_dialog.py
# Dialog for application preferences (font, etc.).

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QPushButton, QColorDialog,
                               QFontComboBox, QSpinBox, QFormLayout, QGroupBox)
from PySide6.QtGui import QFont

class PreferencesDialog(QDialog):
    """
    Allows users to configure application settings like font family,
    font size, and other UI or behavior preferences.
    """
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.parent_window = parent # Store parent for dialogs if needed
        self.settings_manager = settings_manager

        main_layout = QVBoxLayout(self)

        # Font settings group
        font_group_box = QGroupBox("Editor Font")
        form_layout = QFormLayout()

        self.font_combo_box = QFontComboBox()
        form_layout.addRow(QLabel("Font Family:"), self.font_combo_box)

        self.font_size_spin_box = QSpinBox()
        self.font_size_spin_box.setMinimum(6)
        self.font_size_spin_box.setMaximum(72)
        form_layout.addRow(QLabel("Font Size:"), self.font_size_spin_box)
        
        font_group_box.setLayout(form_layout)
        main_layout.addWidget(font_group_box)

        # Bookmark settings group
        bookmark_group_box = QGroupBox("Bookmark Style")
        bookmark_layout = QFormLayout()
        self.bookmark_color_button = QPushButton("Change Bookmark Color")
        self.bookmark_color_button.clicked.connect(self.change_bookmark_color)
        bookmark_layout.addRow(QLabel("Bookmark Color:"), self.bookmark_color_button)
        bookmark_group_box.setLayout(bookmark_layout)
        main_layout.addWidget(bookmark_group_box)

        # Add other preference groups here if needed

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)
        self.load_preferences()

    def load_preferences(self):
        """Loads current preferences from settings_manager and updates UI."""
        font_family = self.settings_manager.get_editor_font_family()
        font_size = self.settings_manager.get_editor_font_size()

        self.font_combo_box.setCurrentFont(QFont(font_family))
        self.font_size_spin_box.setValue(font_size)
        self._update_bookmark_color_button_appearance(self.settings_manager.get_bookmark_color())

    def save_preferences(self):
        """Saves current UI selections to settings_manager."""
        selected_font_family = self.font_combo_box.currentFont().family()
        selected_font_size = self.font_size_spin_box.value()
        # Bookmark color is saved directly in change_bookmark_color via settings_manager

        self.settings_manager.set_editor_font_family(selected_font_family)
        self.settings_manager.set_editor_font_size(selected_font_size)

    def _update_bookmark_color_button_appearance(self, color):
        """Updates the bookmark color button's background to show the selected color."""
        self.bookmark_color_button.setStyleSheet(f"background-color: {color.name()};")
        luminance = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
        text_color = "black" if luminance > 128 else "white"
        self.bookmark_color_button.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")

    def change_bookmark_color(self):
        """Opens a color dialog to change the global bookmark color."""
        current_color = self.settings_manager.get_bookmark_color()
        new_color = QColorDialog.getColor(current_color, self, "Select Bookmark Color")
        if new_color.isValid():
            self.settings_manager.set_bookmark_color(new_color) # Save directly
            self._update_bookmark_color_button_appearance(new_color)
            # Notify BookmarkManager if it's separate and needs to emit a signal
            if hasattr(self.parent_window, 'bookmark_manager'): # Assuming MainWindow is parent
                self.parent_window.bookmark_manager.set_bookmark_color(new_color) # This will emit signal

    def accept(self):
        """Saves preferences and closes the dialog."""
        self.save_preferences()
        super().accept()

    # reject() is handled by QDialogButtonBox by default