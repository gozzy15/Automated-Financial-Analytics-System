import sqlite3

DB_PATH = "financial_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE MIGRATION")
print("=" * 60)

# ---------------------------------------------------
# Create a new table with the correct schema
# ---------------------------------------------------

cursor.execute("""
CREATE TABLE stock_prices_new (

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

print("✓ Created new table")

# ---------------------------------------------------
# Copy unique rows
# ---------------------------------------------------

cursor.execute("""
INSERT OR IGNORE INTO stock_prices_new
SELECT *
FROM stock_prices
ORDER BY Date;
""")

print("✓ Copied unique records")

# ---------------------------------------------------
# Count records
# ---------------------------------------------------

old_count = cursor.execute(
    "SELECT COUNT(*) FROM stock_prices"
).fetchone()[0]

new_count = cursor.execute(
    "SELECT COUNT(*) FROM stock_prices_new"
).fetchone()[0]

print()
print(f"Old table rows : {old_count:,}")
print(f"New table rows : {new_count:,}")
print(f"Duplicates removed : {old_count-new_count:,}")

# ---------------------------------------------------
# Replace old table
# ---------------------------------------------------

cursor.execute("DROP TABLE stock_prices")

cursor.execute(
    "ALTER TABLE stock_prices_new RENAME TO stock_prices"
)

print("✓ Replaced old table")

conn.commit()
conn.close()

print()
print("=" * 60)
print("Migration completed successfully.")
print("=" * 60)