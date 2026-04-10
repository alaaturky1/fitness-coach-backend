from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Support structured extras (record.__dict__ contains many built-ins; whitelist ours)
        for k in ("session_id", "exercise", "rep_count", "issues", "elapsed_ms", "speak", "priority", "path", "method"):
            if k in record.__dict__:
                payload[k] = record.__dict__[k]
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    root.setLevel(settings.log_level)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    # Replace existing handlers (avoid duplicate logs under reload)
    root.handlers = [handler]

