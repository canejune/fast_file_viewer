# FastFileViewer :: core/file_handler.py
# Handles file I/O, asynchronous loading, line storage.

from PySide6.QtCore import QObject, Signal, QThread

class FileLoaderThread(QThread):
    """
    Worker thread for loading file content asynchronously.
    """
    # Signal to emit loaded lines (e.g., a chunk of lines)
    lines_loaded = Signal(list)
    # Signal to emit loading progress (e.g., percentage)
    progress_updated = Signal(int)
    # Signal to emit when loading is finished
    loading_finished = Signal()

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath

    def run(self):
        """
        Load the file content.
        This is a placeholder. Actual implementation will read the file in chunks.
        """
        try:
            # Simulate file loading
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Use read().splitlines() to get lines without trailing newline characters
                lines = f.read().splitlines()
                self.lines_loaded.emit(lines)
                self.progress_updated.emit(100) # Placeholder
        except Exception as e:
            print(f"Error loading file: {e}") # Proper error handling needed
        finally:
            self.loading_finished.emit()

class FileHandler(QObject):
    """
    Manages all aspects of file reading.
    """
    # Signal to emit when the entire file content is ready (list of lines)
    file_content_loaded = Signal(list)
    # Signal to emit when the file loading process (thread) has finished
    loading_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.loader_thread = None

    def load_file(self, filepath):
        """
        Initiates asynchronous loading of the specified file.
        """
        if self.loader_thread and self.loader_thread.isRunning():
            # Handle case where a file is already being loaded
            print("A file is already being loaded.")
            return

        self.lines = [] # Clear previous content
        self.loader_thread = FileLoaderThread(filepath)
        self.loader_thread.lines_loaded.connect(self.on_lines_loaded)
        # self.loader_thread.progress_updated.connect(self.on_progress_updated)
        self.loader_thread.loading_finished.connect(self.on_loading_finished)
        self.loader_thread.start()
        print(f"Started loading file: {filepath}")

    def on_lines_loaded(self, new_lines):
        """
        Slot to receive lines from the loader thread.
        For simplicity, we assume all lines are loaded at once here.
        In a chunked loading scenario, this would append and potentially emit partial updates.
        """
        self.lines = new_lines # Replace content with the new file's lines
        self.file_content_loaded.emit(self.lines)

    # def on_progress_updated(self, progress):
    #     # Notify UI of progress

    def on_loading_finished(self):
        """Slot called when the FileLoaderThread finishes."""
        print("File loading finished.")
        self.loading_finished.emit() # Emit FileHandler's own signal

    def get_line_count(self):
        """Returns the number of loaded lines."""
        return len(self.lines)

    def get_line(self, line_number):
        """Returns the content of a specific line (0-indexed)."""
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        return None