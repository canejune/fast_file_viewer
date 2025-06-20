# FastFileViewer :: ui/editor_view.py
# Central text display area, line numbers, gutters.

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QTextEdit, QAbstractScrollArea, QSizePolicy # QTextEdit for ExtraSelection
from PySide6.QtGui import QFont, QPainter, QColor, QTextCursor, QTextCharFormat # Added QTextCursor and QTextCharFormat
from PySide6.QtCore import Qt, QRect, QSize

from .components.line_number_area import LineNumberArea
# from .components.bookmark_gutter import BookmarkGutter
# from .components.timestamp_gutter import TimestampGutter

# Forward declaration for type hinting if MinimapView is in the same module or imported later
# class MinimapView: pass

class EditorView(QWidget): # Changed from QPlainTextEdit
    """
    Displays the file content with line numbers and other gutter information.
    This widget now contains a QPlainTextEdit and a LineNumberArea.
    """
    def __init__(self, main_window, bookmark_manager, parent=None): # Pass main_window and bookmark_manager
        super().__init__(parent)
        self.main_window = main_window # Store reference to main_window
        self.bookmark_manager = bookmark_manager


        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap) # Important for minimap sync
        self.text_edit.setFont(QFont("Courier New", 10)) # Default font

        self.line_number_area = LineNumberArea(self.text_edit)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0) # Remove margins
        layout.setSpacing(0) # Remove spacing between widgets
        layout.addWidget(self.line_number_area)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # Connect signals for scrollbar changes to update gutters if they exist
        self.text_edit.blockCountChanged.connect(self.update_line_number_area_width)
        self.text_edit.updateRequest.connect(self.update_line_number_area)
        self.text_edit.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)
        # self.text_edit.cursorPositionChanged.connect(self.line_number_area.update) # For current line highlight in gutter

        # Pass bookmark_manager to LineNumberArea and connect signals
        self.line_number_area.set_bookmark_manager(self.bookmark_manager)
        self.bookmark_manager.bookmarks_changed.connect(self.line_number_area.update)

        self.update_line_number_area_width() # Initial width calculation
        self.minimap_view_ref = None # Reference to the minimap

    def update_line_number_area_width(self, _=None): # Parameter can be ignored
        """Updates the width of the line number area."""
        self.line_number_area.updateGeometry() # Triggers sizeHint recalculation and layout update

    def update_line_number_area(self, rect: QRect, dy: int):
        """Scrolls the line number area or updates its content."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            # rect contains the area in the text_edit that needs repaint.
            # We need to update a corresponding area in the line_number_area.
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        # If the viewport itself is part of the update rect (e.g. full repaint)
        if rect.contains(self.text_edit.viewport().rect()):
            self.update_line_number_area_width()

    def link_minimap(self, minimap_view): # minimap_view is of type MinimapView
        """Links this editor view to a minimap view."""
        self.minimap_view_ref = minimap_view
        if self.minimap_view_ref:
            self.minimap_view_ref.scroll_request.connect(self.scroll_to_percentage)
            # Initial update of minimap's visible rect
            self._on_scroll_changed() 



    # --- Methods to forward to self.text_edit ---
    def append_lines(self, lines: list):
        """Appends a list of lines to the editor."""
        self.text_edit.appendPlainText("\n".join(lines))

    def set_text_content(self, lines_list: list):
        """Sets the entire text content of the editor from a list of lines."""
        self.text_edit.clear()
        self.text_edit.setPlainText("\n".join(lines_list))
        # After setting content, update minimap's visible area
        self.update_highlighting() # Update highlighting when new content is set
        self._on_scroll_changed()

    def set_view_font(self, font_family: str, font_size: int):
        """Sets the font for the editor view."""
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        # Font change might affect line number area width and appearance
        self.update_line_number_area_width() # Recalculate width
        self.line_number_area.update()       # Repaint gutter
        if self.minimap_view_ref: # Update minimap if font changes
            self.minimap_view_ref.setFont(font) # Or a scaled version
            self.update_highlighting() # Font change can affect layout, re-highlight
            self._on_scroll_changed()

    def clear(self):
        """Clears the text editor content."""
        self.text_edit.clear()
        if self.minimap_view_ref:
            self.minimap_view_ref.clear_content()

    def _on_scroll_changed(self, value=None): # value can be ignored if not directly used
        """Called when the editor's vertical scrollbar changes."""
        if self.minimap_view_ref:
            self.minimap_view_ref.update_visible_rect(self.text_edit.verticalScrollBar())

    def scroll_to_percentage(self, percentage: float):
        """Scrolls the editor view to a given percentage (0.0 to 1.0)."""
        scrollbar = self.text_edit.verticalScrollBar()
        scroll_range = scrollbar.maximum() - scrollbar.minimum()
        target_value = int(scrollbar.minimum() + scroll_range * percentage)
        scrollbar.setValue(target_value)

    def scroll_to_line(self, line_number_0_indexed: int):
        """Scrolls the editor view to make the specified line number visible."""
        doc = self.text_edit.document()
        if 0 <= line_number_0_indexed < doc.blockCount():
            block = doc.findBlockByNumber(line_number_0_indexed)
            if block.isValid():
                cursor = QTextCursor(block)
                self.text_edit.setTextCursor(cursor) # Moves cursor and scrolls
                self.text_edit.centerCursor() # Tries to center the line

    def update_highlighting(self):
        """Applies regex highlighting based on patterns from RegexEngine."""
        if not hasattr(self.main_window, 'regex_engine'):
            return

        # 1. Clear previous highlighting
        # Clear character format highlighting (text color)
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        default_char_format = QTextCharFormat() # Create a default format
        # If you have a theme-aware default text color, set it here.
        # For now, it will revert to the QPlainTextEdit's default.
        cursor.setCharFormat(default_char_format)
        cursor.clearSelection()

        # Clear extra selections (line background)
        self.text_edit.setExtraSelections([])

        active_patterns = self.main_window.regex_engine.get_active_patterns()
        if not active_patterns:
            #print("[Highlighting] No active patterns.") # DEBUG
            return

        extra_selections = []
        doc = self.text_edit.document()
        # To ensure "맨 위에 검색결과로 배경색을 표시해줘" (first active pattern in list takes precedence for line background)
        # we keep track of lines that already have a background applied by a higher-priority pattern.
        lines_with_background_applied = set()

        # print(f"[Highlighting] Active patterns: {[(p.pattern, fg.name(), bg.name()) for p, fg, bg in active_patterns]}") # DEBUG
        # Iterate through patterns (order in active_patterns matters for background precedence)
        for compiled_regex, fg_color, bg_color in active_patterns:
            block = doc.firstBlock()
            while block.isValid():
                line_number = block.blockNumber()
                line_text = block.text()

                # Apply line background color (if not already applied by a higher priority pattern)
                if line_number not in lines_with_background_applied:
                    # DEBUG: Check for matches for background
                    match_found_for_bg = False
                    for bg_match in compiled_regex.finditer(line_text): # Check if pattern matches anywhere in line
                        selection = QTextEdit.ExtraSelection()
                        selection.format.setBackground(bg_color)
                        selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
                        
                        line_cursor = QTextCursor(block)
                        selection.cursor = line_cursor
                        extra_selections.append(selection)
                        lines_with_background_applied.add(line_number)
                        match_found_for_bg = True
                        #print(f"[Highlighting] BG: Line {line_number + 1} matched by '{compiled_regex.pattern}' (Color: {bg_color.name()}). Match: '{bg_match.group(0)}'") # DEBUG
                        break # Apply background once per line per high-priority pattern
                    # if not match_found_for_bg and line_number < 10: # DEBUG: Check first few non-matching lines for this pattern
                    #     print(f"[Highlighting] BG: Line {line_number + 1} NO match by '{compiled_regex.pattern}' for background.")

                # Apply foreground color to specific matches
                for match in compiled_regex.finditer(line_text):
                    start, end = match.span()
                    match_cursor = QTextCursor(block)
                    match_cursor.setPosition(block.position() + start)
                    match_cursor.setPosition(block.position() + end, QTextCursor.MoveMode.KeepAnchor)
                    
                    char_format = QTextCharFormat()
                    char_format.setForeground(fg_color)
                    # print(f"[Highlighting] FG: Line {line_number + 1} matched by '{compiled_regex.pattern}' (Color: {fg_color.name()}). Text: '{match.group(0)}'") # DEBUG
                    match_cursor.mergeCharFormat(char_format)
                block = block.next()
        self.text_edit.setExtraSelections(extra_selections)
    # Add other QPlainTextEdit methods you need to expose as needed