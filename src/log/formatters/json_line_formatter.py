"""Custom log formatters for JSON."""

import json
import logging
from typing import Any, Dict


class JsonLineFormatter(logging.Formatter):
    """Outputs every log record as one JSON line.

    This is ideal for log aggregation systems like Loki, as each line
    is a complete, parseable JSON object.

    Example output:
    {
      "time": "2025-01-08 10:30:45",
      "level": "INFO",
      "logger": "api_gateway",
      "message": "Request received",
      "correlation_id": "abc-123",
      "trace_id": "xyz-789"
    }
    """

    # Standard LogRecord attributes that we don't want to include as extras
    _STD_ATTRS = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys())

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON line.

        Args:
            record: The log record to format.

        Returns:
            A JSON string representing the log record.
        """
        # Handle dict/list messages differently
        if isinstance(record.msg, (dict, list)):
            msg_val: Any = record.msg
        else:
            msg_val = record.getMessage()

        # Build base payload
        payload: Dict[str, Any] = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": msg_val,
        }

        # Add all extras (including correlation_id, trace_id, span_id if present)
        for k, v in record.__dict__.items():
            if k in self._STD_ATTRS or k in ("msg", "args"):
                continue
            try:
                # Test if value is JSON serializable
                json.dumps(v)
                payload[k] = v
            except Exception:
                # If not, convert to string
                payload[k] = str(v)

        # Add exception info if any
        if record.exc_info:
            try:
                payload["err"] = self.formatException(record.exc_info)
            except Exception:
                import traceback

                payload["err"] = "".join(traceback.format_exception(*record.exc_info))

        return json.dumps(payload, ensure_ascii=False)
