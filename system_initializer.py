#!/usr/bin/env python3
"""Initialize the financial dashboard with sample data"""
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from database_builder import create_database

# Create database
from system_config import DB_PATH

def load_sample_data():
    """Populate the database with sample stock data."""

    with sqlite3.connect(DB_PATH) as conn:

        tickers = [
            "AAPL",
            "GOOGL",
            "MSFT",
            "AMZN",
            "TSLA",
            "META"
        ]

        start_date = datetime.now() - timedelta(days=90)

        # Move the remainder of your existing sample-data code here

        for ticker in tickers:
            dates = []
            current_date = start_date
            while current_date <= datetime.now():
                if current_date.weekday() < 5:  # Weekdays only
                    dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            
            # Generate random but realistic stock data
            np.random.seed(hash(ticker) % 10000)
            n_days = len(dates)
            
            # Base price (realistic ranges)
            base_prices = {
                'AAPL': 180, 'GOOGL': 140, 'MSFT': 380,
                'AMZN': 170, 'TSLA': 240, 'META': 490
            }
            base = base_prices.get(ticker, 100)
            
            # Generate prices with some trend and randomness
            prices = []
            current = base
            for i in range(n_days):
                # Small daily change (±3%)
                change = np.random.normal(0.001, 0.015)
                current = current * (1 + change)
                prices.append(current)
            
            # Create DataFrame
            df = pd.DataFrame({
                'Date': dates,
                'Open': [p * 0.99 for p in prices],  # Open slightly lower
                'High': [p * 1.02 for p in prices],  # High slightly higher
                'Low': [p * 0.98 for p in prices],   # Low slightly lower
                'Close': prices,
                'Volume': np.random.randint(1000000, 50000000, n_days),
                'Ticker': ticker,
                'Processing_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Calculate returns
            df['Daily_Return'] = df['Close'].pct_change()
            df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
            
            # Calculate moving averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            # Calculate RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Fill NaN values
            df = df.bfill().ffill()
            
            # Insert into database
            df.to_sql('stock_prices', conn, if_exists='append', index=False)
            print(f"  ✅ Created sample data for {ticker} ({n_days} days)")

def database_has_data():
    """Return True if stock_prices already contains records."""

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM stock_prices")

        count = cursor.fetchone()[0]

        return count > 0

# Verify data
def verify_database():
    """Display a summary of the database."""

    with sqlite3.connect(DB_PATH) as conn:

        ticker_count = pd.read_sql_query(
            "SELECT COUNT(DISTINCT Ticker) AS count FROM stock_prices",
            conn
        )

        row_count = pd.read_sql_query(
            "SELECT COUNT(*) AS count FROM stock_prices",
            conn
        )

    print("\n📊 Database contains:")
    print(f"   • {ticker_count['count'].iloc[0]} tickers")
    print(f"   • {row_count['count'].iloc[0]} records")

def initialize_system():
    """
    Create the database if needed, load sample
    data when empty, and verify the contents.
    """

    if not os.path.exists(DB_PATH):

        print("📊 Creating database...")

        create_database()

    if not database_has_data():

        print("📈 Loading sample data...")

        load_sample_data()

    else:

        print("✓ Database already contains stock data.")

    verify_database()

if __name__ == "__main__":

    print("=" * 60)
    print("FINANCIAL DASHBOARD INITIALIZATION")
    print("=" * 60)

    initialize_system()

    print("=" * 60)
    print("✓ Initialization completed successfully.")
    print("=" * 60)