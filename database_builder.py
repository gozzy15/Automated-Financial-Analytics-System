#!/usr/bin/env python3
"""Create the SQLite database schema for the Financial Analytics System."""
import sqlite3
import os

from system_config import DB_PATH

def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_PATH)

# Create stock_prices table
def create_stock_prices_table(cursor):
    """Create stock prices table."""

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (

        Date TEXT NOT NULL,

        Open REAL,

        High REAL,

        Low REAL,

        Close REAL,

        Volume INTEGER,

        Daily_Return REAL,

        Cumulative_Return REAL,

        SMA_20 REAL,

        SMA_50 REAL,

        RSI REAL,

        Ticker TEXT NOT NULL,

        Processing_Date TEXT,

        PRIMARY KEY (Date, Ticker)

    )
    """)

# Create predictions table
def create_predictions_table(cursor):

    """Create predictions table."""

    cursor.execute('''
                   
    CREATE TABLE IF NOT EXISTS predictions (
                   
        Prediction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   
        Ticker TEXT,
                   
        Prediction_Date TEXT,
                   
        Predicted_Close REAL,
                   
        Confidence_Interval_Lower REAL,
                   
        Confidence_Interval_Upper REAL,
                   
        Model_Used TEXT,
                   
        Created_At TEXT
                   
    )
                   
    ''')

def create_financial_metrics_table(cursor):

    """Create financial metrics table."""

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_metrics (

        Metric_ID INTEGER PRIMARY KEY AUTOINCREMENT,

        Ticker TEXT,

        Metric_Date TEXT,

        Metric_Name TEXT,

        Metric_Value REAL,

        Created_At TEXT

    )
    """)

def create_indexes(cursor):
    """Create database indexes."""
    cursor.execute("""

        CREATE INDEX IF NOT EXISTS idx_stock_ticker

        ON stock_prices(Ticker)

    """)

    cursor.execute("""

        CREATE INDEX IF NOT EXISTS idx_stock_date

        ON stock_prices(Date)

    """)

def verify_database(connection):

    """Verify that the database schema is correct."""

    cursor = connection.cursor()

    cursor.execute("""

        SELECT name

        FROM sqlite_master

        WHERE type='table'

    """)

    tables = {

        row[0]

        for row in cursor.fetchall()

    }

    required = {

        "stock_prices",

        "predictions",

        "financial_metrics"

    }

    missing = required - tables

    if missing:

        raise RuntimeError(

            f"Missing tables: {missing}"

        )

    print("✓ Database schema verified.")

def create_database():

    """Create the database schema."""

    if os.path.exists(DB_PATH):

        os.remove(DB_PATH)

        print("✓ Removed existing database")

    with get_connection() as connection:

        cursor = connection.cursor()

        create_stock_prices_table(cursor)

        create_predictions_table(cursor)

        create_financial_metrics_table(cursor)

        create_indexes(cursor)

        connection.commit()

        verify_database(connection)

    print("✓ Database created successfully.")



if __name__ == "__main__":
    print("🔧 Creating fresh database...")
    create_database()