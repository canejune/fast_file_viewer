# FastFileViewer :: ui/regex_dialog.py
# Dialog for managing regex patterns.

import uuid
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLineEdit,
                               QListWidget, QListWidgetItem, QCheckBox, QColorDialog, QHBoxLayout,
                               QDialogButtonBox, QGroupBox, QFormLayout, QLabel)
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt

class RegexDialog(QDialog):
    """
    Dialog for users to add, edit, remove, enable/disable
    regular expression patterns for searching and filtering.
    """
    def __init__(self, regex_engine, parent=None): # line_filter removed for now, assuming regex_engine handles notifications
        super().__init__(parent)
        self.setWindowTitle("Manage Regex Patterns")
        self.regex_engine = regex_engine
        # self.line_filter = line_filter # If direct interaction is needed
        self.default_fg_color = QColor(Qt.GlobalColor.black)
        self.default_bg_color = QColor(Qt.GlobalColor.yellow)

        # Internal list to manage patterns during dialog session
        # Each item: {"id": str, "pattern_str": str, "fg_color": QColor, "bg_color": QColor, "is_active": bool}
        self.current_patterns = []
        # Temporary storage for colors of the pattern being edited/added
        self.current_edit_fg_color = self.default_fg_color
        self.current_edit_bg_color = self.default_bg_color

        layout = QVBoxLayout(self)

        # Pattern List
        self.pattern_list_widget = QListWidget()
        self.pattern_list_widget.currentItemChanged.connect(self.on_pattern_selected)
        layout.addWidget(self.pattern_list_widget)

        # Pattern Details GroupBox
        details_group = QGroupBox("Pattern Details")
        details_layout = QFormLayout(details_group)

        self.pattern_input = QLineEdit()
        self.pattern_input.returnPressed.connect(self.handle_pattern_input_enter)
        details_layout.addRow(QLabel("Pattern:"), self.pattern_input)

        self.active_checkbox = QCheckBox("Active")
        details_layout.addRow(self.active_checkbox)

        self.fg_color_button = QPushButton("Change Text Color")
        self.fg_color_button.clicked.connect(self.change_pattern_fg_color)
        details_layout.addRow(QLabel("Text Color:"), self.fg_color_button)

        self.bg_color_button = QPushButton("Change Background Color")
        self.bg_color_button.clicked.connect(self.change_pattern_bg_color)
        details_layout.addRow(QLabel("Background Color:"), self.bg_color_button)

        self._update_color_button_appearance(self.fg_color_button, self.current_edit_fg_color)
        self._update_color_button_appearance(self.bg_color_button, self.current_edit_bg_color)
        layout.addWidget(details_group)

        # Action Buttons
        actions_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New")
        self.add_button.clicked.connect(self.add_new_pattern)
        actions_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update Selected")
        self.update_button.clicked.connect(self.update_selected_pattern)
        self.update_button.setEnabled(False) # Enabled when an item is selected
        actions_layout.addWidget(self.update_button)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_pattern)
        self.remove_button.setEnabled(False) # Enabled when an item is selected
        actions_layout.addWidget(self.remove_button)
        layout.addLayout(actions_layout)

        # Dialog Buttons (OK, Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.load_patterns()

        # If no patterns are loaded, enable detail fields for adding a new one.
        if self.pattern_list_widget.count() == 0:
            self._update_details_state(True)
            self.pattern_input.setFocus()
        # else: on_pattern_selected will handle enabling/disabling fields.

    def _update_color_button_appearance(self, button: QPushButton, color: QColor):
        """Updates a color button's appearance to show the selected color."""
        button.setStyleSheet(f"background-color: {color.name()};")
        # Set text color based on luminance for better readability
        luminance = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
        text_color = "black" if luminance > 128 else "white"
        button.setStyleSheet(f"background-color: {color.name()}; color: {text_color};")

    def _update_details_state(self, enabled: bool):
        """Enables or disables the pattern detail editing fields."""
        self.pattern_input.setEnabled(enabled)
        self.active_checkbox.setEnabled(enabled)
        self.fg_color_button.setEnabled(enabled)
        self.bg_color_button.setEnabled(enabled)
        self.update_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
        if not enabled:
            self.pattern_input.clear()
            self.active_checkbox.setChecked(False)
            # Reset color buttons to transparent or default if details are disabled
            self._update_color_button_appearance(self.fg_color_button, QColor(Qt.GlobalColor.transparent))
            self._update_color_button_appearance(self.bg_color_button, QColor(Qt.GlobalColor.transparent))

    def load_patterns(self):
        """Loads patterns from regex_engine and populates the list widget."""
        self.current_patterns = self.regex_engine.get_patterns() # Expects list of dicts
        self.pattern_list_widget.clear()
        for pattern_data in self.current_patterns:
            item = QListWidgetItem(pattern_data["pattern_str"])
            item.setData(Qt.ItemDataRole.UserRole, pattern_data["id"]) # Store ID for mapping
            # Optionally, set item font/color based on active state or color
            font = item.font()
            font.setStrikeOut(not pattern_data["is_active"])
            item.setFont(font)
            # List item foreground uses fg_color. Background is harder to set per item simply.
            item.setForeground(pattern_data["fg_color"] if pattern_data["is_active"] else Qt.GlobalColor.gray)
            self.pattern_list_widget.addItem(item)

        if self.pattern_list_widget.count() > 0:
            self.pattern_list_widget.setCurrentRow(0) # Select the first item if list is not empty
        else: # No patterns loaded
             self._update_details_state(True) # Enable fields for adding new pattern

    def on_pattern_selected(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        """Handles selection changes in the pattern list."""
        if not current_item:
            self._update_details_state(False)
            return

        pattern_id = current_item.data(Qt.ItemDataRole.UserRole)
        pattern_data = next((p for p in self.current_patterns if p["id"] == pattern_id), None)

        if pattern_data:
            self.pattern_input.setText(pattern_data["pattern_str"])
            self.active_checkbox.setChecked(pattern_data["is_active"])
            self.current_edit_fg_color = pattern_data["fg_color"]
            self.current_edit_bg_color = pattern_data["bg_color"]
            self._update_color_button_appearance(self.fg_color_button, self.current_edit_fg_color)
            self._update_color_button_appearance(self.bg_color_button, self.current_edit_bg_color)
            self._update_details_state(True)
        else:
            self._update_details_state(False) # Should not happen if IDs are consistent

    def add_new_pattern(self):
        """Adds a new pattern based on current input field content."""
        # Ensure fields are enabled if somehow they got disabled and user clicks "Add New"
        if not self.pattern_input.isEnabled():
            self._update_details_state(True)
            self.pattern_input.setFocus()
            # If input was disabled, it's unlikely to have text, so we might return here
            # or let the logic below handle the empty string.

        pattern_str = self.pattern_input.text().strip()
        if not pattern_str:
            self.pattern_input.setFocus() # If empty, just focus to encourage typing
            return

        # Use colors currently set for editing
        new_pattern = {
            "id": str(uuid.uuid4()), # Unique ID for the pattern
            "pattern_str": pattern_str,
            "fg_color": self.current_edit_fg_color,
            "bg_color": self.current_edit_bg_color,
            "is_active": self.active_checkbox.isChecked()
        }
        self.current_patterns.append(new_pattern)
        self.refresh_list_widget()
        # Select the newly added item
        for i in range(self.pattern_list_widget.count()):
            if self.pattern_list_widget.item(i).data(Qt.ItemDataRole.UserRole) == new_pattern["id"]:
                self.pattern_list_widget.setCurrentRow(i)
                break
        # on_pattern_selected will update edit fields with the new pattern's details

    def update_selected_pattern(self):
        """Updates the currently selected pattern with data from input fields."""
        current_item = self.pattern_list_widget.currentItem()
        if not current_item:
            return

        pattern_id = current_item.data(Qt.ItemDataRole.UserRole)
        pattern_data = next((p for p in self.current_patterns if p["id"] == pattern_id), None)

        if pattern_data:
            pattern_data["pattern_str"] = self.pattern_input.text().strip()
            pattern_data["is_active"] = self.active_checkbox.isChecked()
            pattern_data["fg_color"] = self.current_edit_fg_color
            pattern_data["bg_color"] = self.current_edit_bg_color

            if not pattern_data["pattern_str"]:
                # Optionally prevent empty pattern string or handle as removal
                return
            self.refresh_list_widget() # Refresh to show changes (e.g., strikethrough)

    def remove_selected_pattern(self):
        """Removes the currently selected pattern."""
        current_item = self.pattern_list_widget.currentItem()
        if not current_item:
            return

        pattern_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.current_patterns = [p for p in self.current_patterns if p["id"] != pattern_id]
        self.refresh_list_widget()
        # If list becomes empty, ensure input fields are enabled for adding a new pattern
        if self.pattern_list_widget.count() == 0:
            self._update_details_state(True)
            self.pattern_input.clear() # Clear details of the removed item
            self.active_checkbox.setChecked(True)
            self.current_edit_fg_color = self.default_fg_color
            self.current_edit_bg_color = self.default_bg_color
            self._update_color_button_appearance(self.fg_color_button, self.current_edit_fg_color)
            self._update_color_button_appearance(self.bg_color_button, self.current_edit_bg_color)
            self.pattern_input.setFocus()

    def change_pattern_fg_color(self):
        """Opens a color dialog to change the pattern's foreground (text) color."""
        initial_color = self.current_edit_fg_color
        current_item = self.pattern_list_widget.currentItem()
        if current_item: # Editing existing
            pattern_id = current_item.data(Qt.ItemDataRole.UserRole)
            pattern_data = next((p for p in self.current_patterns if p["id"] == pattern_id), None)
            if pattern_data: initial_color = pattern_data["fg_color"]

        new_color = QColorDialog.getColor(initial_color, self, "Select Text Color")
        if new_color.isValid():
            self.current_edit_fg_color = new_color
            self._update_color_button_appearance(self.fg_color_button, new_color)
            if current_item and pattern_data: # If editing an existing item, update its data immediately
                pattern_data["fg_color"] = new_color
                self.refresh_list_widget() # Update list item appearance

    def change_pattern_bg_color(self):
        """Opens a color dialog to change the pattern's background color."""
        initial_color = self.current_edit_bg_color
        current_item = self.pattern_list_widget.currentItem()
        if current_item: # Editing existing
            pattern_id = current_item.data(Qt.ItemDataRole.UserRole)
            pattern_data = next((p for p in self.current_patterns if p["id"] == pattern_id), None)
            if pattern_data: initial_color = pattern_data["bg_color"]

        new_color = QColorDialog.getColor(initial_color, self, "Select Background Color")
        if new_color.isValid():
            self.current_edit_bg_color = new_color
            self._update_color_button_appearance(self.bg_color_button, new_color)
            if current_item and pattern_data: # If editing an existing item, update its data immediately
                pattern_data["bg_color"] = new_color
                # Background color of list item is not easily changed, so no refresh needed for that

    def refresh_list_widget(self):
        """Helper to reload the list widget from self.current_patterns."""
        current_selected_id = None
        if self.pattern_list_widget.currentItem():
            current_selected_id = self.pattern_list_widget.currentItem().data(Qt.ItemDataRole.UserRole)

        self.pattern_list_widget.clear()
        for pattern_data in self.current_patterns:
            item = QListWidgetItem(pattern_data["pattern_str"])
            item.setData(Qt.ItemDataRole.UserRole, pattern_data["id"])
            font = item.font()
            font.setStrikeOut(not pattern_data["is_active"])
            item.setFont(font)
            item.setForeground(pattern_data["fg_color"] if pattern_data["is_active"] else Qt.GlobalColor.gray)
            self.pattern_list_widget.addItem(item)
            if pattern_data["id"] == current_selected_id:
                self.pattern_list_widget.setCurrentItem(item) # Restore selection

        if not self.pattern_list_widget.currentItem() and self.pattern_list_widget.count() > 0:
            self.pattern_list_widget.setCurrentRow(0)
        elif self.pattern_list_widget.count() == 0:
             self._update_details_state(True)
             self.pattern_input.clear()
             self.active_checkbox.setChecked(True)
             self.current_edit_fg_color = self.default_fg_color
             self.current_edit_bg_color = self.default_bg_color
             self._update_color_button_appearance(self.fg_color_button, self.current_edit_fg_color)
             self._update_color_button_appearance(self.bg_color_button, self.current_edit_bg_color)
             self.pattern_input.setFocus()

    def handle_pattern_input_enter(self):
        """Handles Enter key press in the pattern input field."""
        pattern_str = self.pattern_input.text().strip()
        if not pattern_str:
            return # Do nothing if pattern is empty

        current_list_item = self.pattern_list_widget.currentItem()
        if current_list_item:
            # If an item is selected, update it
            self.update_selected_pattern()
        else:
            # If no item is selected, add a new pattern
            self.add_new_pattern()
            # After adding, the new item will be selected and its details loaded.
            # If you want to clear input for the *next* new pattern:
            # self.pattern_input.clear()
            # self.active_checkbox.setChecked(True)
            # self.current_edit_fg_color = self.default_fg_color
            # self.current_edit_bg_color = self.default_bg_color
            # self._update_color_button_appearance(self.fg_color_button, self.current_edit_fg_color)
            # self._update_color_button_appearance(self.bg_color_button, self.current_edit_bg_color)
            # self.pattern_list_widget.clearSelection() # So next Enter is also an add
            # self.pattern_input.setFocus()
    def accept(self):
        """Saves changes back to regex_engine and closes the dialog."""
        self.regex_engine.set_patterns(self.current_patterns)
        super().accept()

    # reject() is handled by QDialogButtonBox by default, no changes needed

    # Example of how regex_engine might look (conceptual, not part of this file)
    # class RegexEngine:
    #     def __init__(self):
    #         self.patterns = [] # List of {"id": str, "pattern_str": str, "color": QColor, "is_active": bool}
    #
    #     def get_patterns(self):
    #         return [p.copy() for p in self.patterns] # Return copies to avoid direct modification
    #
    #     def set_patterns(self, new_patterns_data):
    #         self.patterns = [p.copy() for p in new_patterns_data]
    #         # Here, you would typically emit a signal that patterns have changed
    #         # so other parts of the application (like editor_view for highlighting) can update.
    #         print(f"RegexEngine patterns updated: {self.patterns}")