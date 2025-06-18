# Fast File Viewer

## Overview
A high-performance file viewer application developed in Python, designed to efficiently open and analyze large files.
This viewer aims to enhance productivity for developers, data analysts, and system administrators by providing instant file loading, powerful regex-based search and highlighting, and a user-friendly interface.
The entire development process adheres to SOLID principles, and all code comments are written in English.

## Core Features

### 1. Asynchronous File Loading
- **Fast Initial Display**: Instantly loads and displays the beginning of the file to the user.
- **Background Loading**: The rest of the file is progressively loaded in a background thread, preventing UI freezes.
- **Dynamic UI Updates**: Scrollbars and the document overview (Minimap) are updated in real-time as the file loads.

### 2. User Interface (UI)
- **Line Numbers**: Displays unique line numbers to the left of each line, with gutter size adjusting based on file length.
- **Font Adjustment**: Users can freely change the editor's font family and size via the "Edit" -> "Preferences" menu, and settings are saved.
- **Recent Files List**: Provides a list of recently opened files through the "File" -> "Recent Files" menu, which persists across application restarts. The list can be cleared using the "Clear Recent Files" feature.
- **Text Selection and Copy**: Document editing is disabled, but users can select text with the mouse and copy it to the clipboard.
- **Drag and Drop**: Files can be opened by dragging and dropping them onto the application window.
- **Status Bar**: Appropriately displays file loading status and other information in the status bar.
- **Line Ending Handling**: Consistently handles line break characters from various operating systems (Unix, DOS/Windows) to prevent blank line issues.

### 3. Regex Search and Highlighting
- **Multiple Regex Support**: Apply multiple regular expression patterns simultaneously.
- **Custom Colors**: Users can specify custom highlight colors (foreground and background) for each regex pattern.
- **Pattern Management Window**: Manage a list of regular expressions in a separate window, allowing activation/deactivation of each pattern.
- **Minimap Integration**: Lines matching active regex patterns are also indicated with their respective background colors in the minimap.
- **Pattern Precedence**: If multiple active patterns match the same line, the background color of the pattern listed higher in the management dialog will be applied.
- **Persistent Patterns**: Defined regex patterns and their styles are saved and will be available on subsequent application launches.

### 4. Document Overview (Minimap)
- **Full Document Visualization**: Displays a thumbnail (Minimap) of the entire document on the right side of the screen.
- **Navigation**: Instantly navigate to specific parts of the document by clicking or dragging on the Minimap.
- **Accurate Visible Area Indicator**: The currently visible area in the editor is accurately indicated on the Minimap, even for short files.
- **Information Visualization**: Regex search results (line backgrounds) are displayed in the overview with their specified colors.

### 5. Persistent Settings
- Remembers recent files.
- Saves editor font preferences.
- Saves custom regex patterns and their styles.

## Technical Architecture
- **Language and Framework**: Python 3, PySide6 (for UI and multi-threading support)
- **Design Principles**: SOLID principles (Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)

## Module Structure
The application is organized into the following main packages:
- `core/`: Core business logic and data processing modules (e.g., `file_handler.py`, `regex_engine.py`, `settings_manager.py`)
- `ui/`: All PySide6-based user interface components (e.g., `main_window.py`, `editor_view.py`, `minimap_view.py`)
- `utils/`: Utility functions, constants, and helper classes

## Development Guidelines
- **Code Style**: Adherence to PEP 8 coding conventions.
- **Comments**: All code comments and commit messages are written in English.
- **Version Control**: Git.

## Getting Started / How to Run
The application can be run from the project's root directory using the following command.
You can also pass a file path as an argument to open a specific file immediately.
```bash
python main.py [optional_filepath]
```
Example:
```bash
python main.py
python main.py /path/to/your/file.log
```

## TODO / Future Enhancements
- **Bookmark Feature**:
    - Add/remove bookmarks for specific lines.
    - Visual indication for bookmarked lines (e.g., 📖 icon) in the gutter and minimap.
- **Show Only Matching Lines**: Provide a separate results window to display only lines matching regex.
- **Line Filtering**: Hide lines in the main view that match a user-specified regex (while maintaining original line numbers).
- **Timestamp Parsing (Optional)**: Automatically parse timestamps in a specific format within lines, allowing users to define parsing rules and output formats.
- More advanced minimap rendering (e.g., actual tiny text instead of line indicators).
- Horizontal scrolling synchronization between editor and minimap (if line wrapping is off).
- Performance improvements for extremely large files (virtual scrolling for minimap if needed).
- More robust error handling and user feedback.
- Configurable colors for UI elements (theme support).