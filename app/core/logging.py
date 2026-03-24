import json
import logging
from datetime import datetime, UTC


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = [
            "request_id",
            "event",
            "method",
            "path",
            "status_code",
            "duration_ms",
            "upload_filename",
            "content_type",
            "size_bytes",
            "max_upload_mb",
            "reason",
            "scene_hint",
            "scene_type",
            "confidence",
            "has_calories",
            "warnings",
            "user_name",
        ]

        for field in extra_fields:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.handlers = [handler]