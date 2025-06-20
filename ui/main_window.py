# FastFileViewer :: ui/main_window.py
# Main application window, layout, menus, status bar.

import functools
from PySide6.QtWidgets import (QMainWindow, QHBoxLayout, QWidget, QFileDialog, QDialog, QMenu,
                               QMenuBar, QStatusBar, QSplitter)
from PySide6.QtGui import QAction, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt

from .editor_view import EditorView
from .minimap_view import MinimapView
from .regex_dialog import RegexDialog
from .preferences_dialog import PreferencesDialog
from .search_results_window import SearchResultsWindow # Import the new window

from core.file_handler import FileHandler
from core.settings_manager import SettingsManager
from core.regex_engine import RegexEngine
from core.bookmark_manager import BookmarkManager

class MainWindow(QMainWindow):
    """
    The main application window.
    """
    def __init__(self, initial_filepath: str = None):
        super().__init__()
        self.setWindowTitle("Fast File Viewer")
        self.setGeometry(100, 100, 1000, 700) # x, y, width, height

        # Core components
        self.settings_manager = SettingsManager(self)
        self.file_handler = FileHandler(self)
        self.regex_engine = RegexEngine(self.settings_manager, self) # Pass SettingsManager
        self.bookmark_manager = BookmarkManager(self.settings_manager, self)
        self.current_filepath = None # To store the path of the file being loaded/opened
        self.search_results_window = None # Placeholder for the results window instance

        # Central Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget) # Use QHBoxLayout for Editor and Minimap
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Splitter to allow resizing between editor and minimap
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.editor_view = EditorView(self, self.bookmark_manager, self) # Pass self (MainWindow) and bookmark_manager
        splitter.addWidget(self.editor_view)

        self.minimap_view = MinimapView(self.regex_engine, self.bookmark_manager, self) # Pass regex_engine and bookmark_manager
        splitter.addWidget(self.minimap_view)
        
        # Set initial sizes for splitter (optional)
        splitter.setSizes([800, 200]) # Adjust as needed
        main_layout.addWidget(splitter)

        self._create_menus()
        self._create_status_bar()

        # Connect signals from core components to UI updates
        self.file_handler.file_content_loaded.connect(self.minimap_view.set_document_content)
        self.file_handler.file_content_loaded.connect(self.editor_view.set_text_content)
        self.file_handler.loading_finished.connect(self._on_file_loading_finished)
        self.regex_engine.patterns_changed.connect(self.minimap_view.update_styles) # Connect to minimap
        self.regex_engine.patterns_changed.connect(self.editor_view.update_highlighting)
        self.bookmark_manager.bookmark_color_changed.connect(self.minimap_view.update_styles) # Update minimap on bookmark color change
        self.bookmark_manager.bookmarks_changed.connect(self.minimap_view.update_styles) # Update minimap on bookmark change
        self._update_recent_files_menu() # Populate recent files menu at startup
        self.setAcceptDrops(True) # Enable drag and drop for the main window
        self.apply_editor_font_settings() # Apply initial font settings

        if initial_filepath:
            # Ensure minimap also gets content if loaded from command line
            # This might need a slight refactor if _open_initial_file doesn't trigger
            # file_content_loaded in a way that minimap can receive it before first paint.
            # For now, assuming file_content_loaded will be emitted.
            self._open_initial_file(initial_filepath)
        
        # Link editor view and minimap view
        self.editor_view.link_minimap(self.minimap_view)

    def _create_menus(self):
        """Creates the main menu bar and menus."""
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open File...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        self.recent_files_menu = QMenu("Recent Files", self)
        file_menu.addMenu(self.recent_files_menu)

        clear_recent_action = QAction("Clear Recent Files", self)
        clear_recent_action.setStatusTip("Clear the list of recently opened files")
        clear_recent_action.triggered.connect(self._clear_recent_files_action)
        # Add it before the separator for recent files, or after if preferred
        file_menu.addAction(clear_recent_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu (or View/Tools menu for Preferences)
        edit_menu = menu_bar.addMenu("&Edit")
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setStatusTip("Configure application preferences")
        # You can add a shortcut if desired, e.g., QKeySequence.fromString("Ctrl+,")
        preferences_action.triggered.connect(self.open_preferences_dialog)
        edit_menu.addAction(preferences_action)
        
        clear_bookmarks_action = QAction("Clear Bookmarks for Current File", self)
        clear_bookmarks_action.setStatusTip("Remove all bookmarks from the currently open file")
        clear_bookmarks_action.triggered.connect(self._clear_current_file_bookmarks)
        edit_menu.addAction(clear_bookmarks_action)

        # Tools Menu (for Regex Dialog)
        tools_menu = menu_bar.addMenu("&Tools")
        manage_regex_action = QAction("&Manage Regex Patterns...", self)
        manage_regex_action.setStatusTip("Add, edit, or remove regex patterns for highlighting")
        manage_regex_action.triggered.connect(self.open_regex_dialog)
        tools_menu.addAction(manage_regex_action)

        # View Menu
        view_menu = menu_bar.addMenu("&View")
        show_matches_action = QAction("Show Matched & Bookmarked Lines", self)
        show_matches_action.triggered.connect(self.show_matched_bookmarked_lines_window)
        view_menu.addAction(show_matches_action)


    def _create_status_bar(self):
        """Creates the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 3000) # Message disappears after 3 seconds

    def open_file_dialog(self):
        """Opens a dialog to select a file and loads it."""
        filepath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt);;Log Files (*.log)")
        if filepath:
            self._load_file_action(filepath)

    def open_preferences_dialog(self):
        """Opens the preferences dialog."""
        dialog = PreferencesDialog(self.settings_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.apply_editor_font_settings()
            self.status_bar.showMessage("Preferences updated.", 3000)

    def open_regex_dialog(self):
        """Opens the regex management dialog."""
        # Pass the regex_engine instance to the dialog
        dialog = RegexDialog(self.regex_engine, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Regex patterns were updated in regex_engine by the dialog's accept()
            self.status_bar.showMessage("Regex patterns updated.", 3000)
            # self.editor_view.update_highlighting() # No longer needed due to signal/slot

    def apply_editor_font_settings(self):
        """Applies font settings from SettingsManager to EditorView."""
        font_family = self.settings_manager.get_editor_font_family()
        font_size = self.settings_manager.get_editor_font_size()
        self.editor_view.set_view_font(font_family, font_size)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handles drag enter events to accept file drops."""
        if event.mimeData().hasUrls():
            # Check if there's at least one local file URL
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event: QDropEvent):
        """Handles drop events to open the dropped file(s)."""
        urls = event.mimeData().urls()
        if urls:
            filepath_to_open = None
            for url in urls:
                if url.isLocalFile():
                    filepath_to_open = url.toLocalFile()
                    break # Open the first valid local file
            
            if filepath_to_open:
                self._load_file_action(filepath_to_open)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _update_recent_files_menu(self):
        """Clears and repopulates the 'Recent Files' menu."""
        self.recent_files_menu.clear()
        recent_files = self.settings_manager.get_recent_files()

        if not recent_files:
            self.recent_files_menu.setEnabled(False)
            return

        self.recent_files_menu.setEnabled(True)
        for i, filepath in enumerate(recent_files):
            action_text = f"&{i+1} {filepath}"
            action = QAction(action_text, self)
            # Use functools.partial to pass the filepath to the slot
            action.triggered.connect(functools.partial(self._open_recent_file_action, filepath))
            self.recent_files_menu.addAction(action)

    def _open_recent_file_action(self, filepath: str):
        """Handles opening a file selected from the 'Recent Files' menu."""
        self._load_file_action(filepath)

    def _clear_recent_files_action(self):
        """Clears all recent files from settings and updates the menu."""
        self.settings_manager.clear_recent_files()
        self._update_recent_files_menu()
        self.status_bar.showMessage("Recent files list cleared.", 3000)

    def _clear_current_file_bookmarks(self):
        """Clears all bookmarks for the current file."""
        if self.current_filepath:
            self.bookmark_manager.clear_bookmarks_for_current_file()
            self.status_bar.showMessage(f"Bookmarks cleared for {self.current_filepath}", 3000)
        else:
            self.status_bar.showMessage("No file open to clear bookmarks from.", 3000)

    def _on_file_loading_finished(self):
        """Updates the status bar when file loading is complete."""
        if self.current_filepath:
            self.status_bar.showMessage(f"Loaded: {self.current_filepath}", 5000) # Show for 5 seconds
            # self.current_filepath = None # Optionally reset if needed
        else:
            self.status_bar.showMessage("Ready", 3000)

    def _load_file_action(self, filepath: str):
        """Helper method to open and load a file."""
        self.editor_view.clear()
        self.bookmark_manager.set_current_file(filepath) # Set current file for bookmarks
        self.current_filepath = filepath
        self.status_bar.showMessage(f"Opening {filepath}...")
        self.file_handler.load_file(filepath)
        self.settings_manager.add_recent_file(filepath)
        self._update_recent_files_menu()

    def _open_initial_file(self, filepath: str):
        """Loads the initial file passed via command line argument."""
        # This method ensures the file is loaded after the window is fully initialized.
        self._load_file_action(filepath)

    def show_matched_bookmarked_lines_window(self):
        """Gathers matched and bookmarked lines and displays them in a separate window."""
        if not self.current_filepath or not self.file_handler.lines:
            self.status_bar.showMessage("No file loaded or file is empty.", 3000)
            return

        # Using a dictionary to collect results per line, allowing easy merging
        # Key: line_number_0_indexed
        # Value: {"text": str, "types": set, "fg_color": QColor, "bg_color": QColor}
        line_results_map = {}
        all_lines = self.file_handler.lines

        # Collect bookmarked lines
        bookmarked_lines_indices = self.bookmark_manager.get_all_bookmarks()
        bookmark_color = self.bookmark_manager.get_bookmark_color()
        for line_idx in bookmarked_lines_indices:
            if 0 <= line_idx < len(all_lines):
                if line_idx not in line_results_map:
                    line_results_map[line_idx] = {
                        "text": all_lines[line_idx],
                        "types": set(),
                        "fg_color": None, # Default text color for bookmark-only lines
                        "bg_color": bookmark_color # Bookmark color as background
                    }
                line_results_map[line_idx]["types"].add("Bookmark")
                # If only bookmarked, ensure bg_color is bookmark_color
                if not line_results_map[line_idx].get("is_regex_match"):
                     line_results_map[line_idx]["bg_color"] = bookmark_color

        # Collect regex matches
        active_patterns = self.regex_engine.get_active_patterns()
        if active_patterns:
            for line_idx, line_text in enumerate(all_lines):
                for compiled_regex, fg_color, bg_color in active_patterns:
                    if compiled_regex.search(line_text):
                        if line_idx not in line_results_map:
                            line_results_map[line_idx] = {
                                "text": line_text,
                                "types": set(),
                                "fg_color": fg_color,
                                "bg_color": bg_color
                            }
                        else: # Line already in map (e.g., from bookmark), update colors if regex takes precedence
                            line_results_map[line_idx]["fg_color"] = fg_color
                            line_results_map[line_idx]["bg_color"] = bg_color # Regex bg overrides bookmark bg for display
                        
                        line_results_map[line_idx]["types"].add(f"Regex: {compiled_regex.pattern}")
                        line_results_map[line_idx]["is_regex_match"] = True # Mark that regex matched for color precedence
                        break # Add line once per regex match for this purpose
        
        # Convert map to sorted list for display
        final_results_for_display = []
        for line_idx in sorted(line_results_map.keys()):
            data = line_results_map[line_idx]
            # Join types like "Bookmark, Regex: error"
            type_str = ", ".join(sorted(list(data["types"])))
            final_results_for_display.append((line_idx, data["text"], type_str, data["fg_color"], data["bg_color"]))

        if not self.search_results_window:
            self.search_results_window = SearchResultsWindow(self) # Pass MainWindow as parent
        self.search_results_window.display_results(final_results_for_display)
        self.search_results_window.show()
        self.search_results_window.activateWindow() # Bring to front