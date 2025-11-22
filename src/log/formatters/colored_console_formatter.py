"""Custom log formatters for colored console output."""

import json
import logging


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter that displays logs in an easy-to-read format.

    Main line: timestamp | level | logger | message
    Extra fields on separate lines as "key": value

    This makes it easy to see what's happening at a glance during development.
    """

    _STD_ATTRS = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys())

    # ANSI color codes for different log levels
    COLORS = {
        "DEBUG": "\033[36m",  # cyan
        "INFO": "\033[32m",  # green
        "WARNING": "\033[33m",  # yellow
        "ERROR": "\033[31m",  # red
        "CRITICAL": "\033[31;47m",  # red text on white background
    }
    CYAN = "\033[36m"
    PURPLE = "\033[35m"
    THIN_WHITE = "\033[37m"
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors.

        Args:
            record: The log record to format.

        Returns:
            A colored string representing the log record.
        """
        # Get message
        if isinstance(record.msg, (dict, list)):
            msg_val = json.dumps(record.msg, ensure_ascii=False)
        else:
            msg_val = record.getMessage()

        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Get colors
        level_color = self.COLORS.get(record.levelname, "")

        # Main log line with color coding
        main_line = (
            f"{self.CYAN}{timestamp} {level_color}│{self.RESET} "
            f"{level_color}{record.levelname:<8}{self.RESET} {level_color}│{self.RESET} "
            f"{self.PURPLE}{record.name:<15}{level_color}│{self.RESET} "
            f"{msg_val} "
            f"{self.RESET}"
        )

        lines = [main_line]

        # Collect extra fields
        extra_fields = []
        for k, v in record.__dict__.items():
            if k in self._STD_ATTRS or k in ("msg", "args"):
                continue
            extra_fields.append((k, v))

        # Format extra fields with tree-like connectors
        for i, (k, v) in enumerate(extra_fields):
            try:
                if isinstance(v, (dict, list)):
                    value_str = json.dumps(v, ensure_ascii=False)
                else:
                    value_str = str(v)

                # Use └─ for last item, ├─ for others
                connector = "└─" if i == len(extra_fields) - 1 else "├─"
                lines.append(f'    {self.THIN_WHITE}{connector} "{k}": {value_str}{self.RESET}')
            except Exception:
                connector = "└─" if i == len(extra_fields) - 1 else "├─"
                lines.append(f'    {self.THIN_WHITE}{connector} "{k}": {str(v)}{self.RESET}')

        # Add exception info if any
        if record.exc_info:
            try:
                exc_text = self.formatException(record.exc_info)
                lines.append(f"{self.COLORS['ERROR']}{exc_text}{self.RESET}")
            except Exception:
                import traceback

                exc_text = "".join(traceback.format_exception(*record.exc_info))
                lines.append(f"{self.COLORS['ERROR']}{exc_text}{self.RESET}")

        return "\n".join(lines)
