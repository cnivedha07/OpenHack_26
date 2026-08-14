import logging
import sys
from collections import deque
from typing import List

# Rolling in-memory log buffer for live log streaming via API
MAX_LOG_ENTRIES = 200
log_buffer = deque(maxlen=MAX_LOG_ENTRIES)


class RollingBufferHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            log_buffer.append(msg)
        except Exception:
            self.handleError(record)


def setup_logger(name: str = "TrustFed"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Rolling buffer handler
        buffer_handler = RollingBufferHandler()
        buffer_handler.setFormatter(formatter)
        logger.addHandler(buffer_handler)

    return logger


logger = setup_logger()


def log_event(message: str, level: str = "info"):
    """Utility to log an event directly into the rolling buffer."""
    if level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.info(message)


def get_recent_logs(limit: int = 50) -> List[str]:
    """Returns the most recent log lines from the rolling buffer."""
    logs = list(log_buffer)
    return logs[-limit:] if logs else ["System initialized. Monitoring TrustFed FL Pipeline."]
