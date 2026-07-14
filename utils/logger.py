import logging
from pathlib import Path

from system_config import LOG_FOLDER, LOG_FILE

# ==========================================================
# Create logs directory if it doesn't exist
# ==========================================================

LOG_DIR = Path(LOG_FOLDER)
LOG_DIR.mkdir(exist_ok=True)

# ==========================================================
# Configure logger
# ==========================================================

logger = logging.getLogger("financial_dashboard")

if not logger.handlers:

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    # Console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File output
    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)