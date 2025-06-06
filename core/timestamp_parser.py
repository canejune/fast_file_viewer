# FastFileViewer :: core/timestamp_parser.py
# Parses timestamps from lines.

import re
from datetime import datetime
from PySide6.QtCore import QObject

class TimestampParser(QObject):
    """
    Parses timestamps from lines based on user-configurable regex patterns
    and format strings.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parsing_rule_regex = None # User-defined regex to find timestamp
        self.datetime_format = None    # User-defined strptime format
        self.output_format = None      # User-defined strftime format for display

    def set_parsing_rules(self, rule_regex_str, dt_format, out_format):
        """Sets the rules for parsing timestamps."""
        try:
            self.parsing_rule_regex = re.compile(rule_regex_str)
            self.datetime_format = dt_format
            self.output_format = out_format
        except re.error as e:
            print(f"Invalid timestamp parsing regex: {e}")
            self.parsing_rule_regex = None

    def parse_timestamp(self, text_line):
        """
        Parses a timestamp from the line if rules are set and a match is found.
        Returns the formatted timestamp string or None.
        """
        if not self.parsing_rule_regex or not self.datetime_format or not self.output_format:
            return None

        match = self.parsing_rule_regex.search(text_line)
        if match:
            try:
                timestamp_str = match.group(1) # Assuming first group is the timestamp
                dt_obj = datetime.strptime(timestamp_str, self.datetime_format)
                return dt_obj.strftime(self.output_format)
            except (ValueError, IndexError) as e:
                # print(f"Error parsing timestamp from '{text_line}': {e}")
                return None # Or some error indicator
        return None