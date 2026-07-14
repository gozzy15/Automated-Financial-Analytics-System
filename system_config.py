#!/usr/bin/env python3
"""Central configuration settings for the Financial Analytics System."""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Drive Configuration
GDRIVE_CREDENTIALS = os.getenv('GDRIVE_CREDENTIALS_PATH')
GDRIVE_FOLDER_ID = os.getenv('GDRIVE_FOLDER_ID')

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
HR_EMAILS = [
    email.strip()
    for email in os.getenv(
        "HR_EMAILS",
        ""
    ).split(",")
    if email.strip()
]

# =========================
# Database
# =========================
DB_PATH = os.getenv(
    "DB_PATH",
    "financial_data.db"
)

# =========================
# Data directories
# =========================
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "data", "clean")
PROCESSED_DATA_PATH  = os.path.join(CLEAN_DATA_PATH, "processed_tickers_historical_data")
REPORTS_PATH = os.path.join(
    CLEAN_DATA_PATH,
    "spreadsheet_reports"
)

# Scraping Configuration
SCRAPE_INTERVAL = int(
    os.getenv("SCRAPE_INTERVAL", 7)
)
LIVE_UPDATE_SECONDS = int(
    os.getenv("LIVE_UPDATE_SECONDS", 30)
)
FINANCIAL_SOURCES = {
    'yahoo_finance': 'https://finance.yahoo.com/',
    'marketwatch': 'https://www.marketwatch.com/'
}
MODELS_PATH = os.path.join(
    BASE_DIR,
    "models"
)

# Dash Configuration
DASH_PORT = 8050
DASH_DEBUG = True

# Logging Configuration
LOG_FOLDER = os.path.join(
    BASE_DIR,
    "logs"
)
LOG_FILE = os.path.join(
    LOG_FOLDER,
    "dashboard.log"
)

# Default date range for data retrieval
DEFAULT_DAYS = int(
    os.getenv("DEFAULT_DAYS", 30)
)

DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL",
    "Random Forest"
)