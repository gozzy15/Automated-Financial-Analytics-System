import sqlite3
import pandas as pd
import os

from datetime import datetime
from system_config import DB_PATH, DEFAULT_MODEL, REPORTS_PATH
from utils.logger import logger


class DatabaseHandler:
    def __init__(self):
        self.db_path = DB_PATH

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:

            with self.get_connection() as conn:

                if params:
                    return pd.read_sql_query(
                        query,
                        conn,
                        params=params
                    )

                return pd.read_sql_query(
                    query,
                    conn
                )

        except Exception:

            logger.exception(
                "Database query failed."
            )

            raise

    def get_stock_data(
        self,
        ticker: str,
        start_date: str = None,
        end_date: str = None
    ):
        """Get stock data for specific ticker and date range"""

        query = "SELECT * FROM stock_prices WHERE Ticker = ?"
        params = [ticker]

        if start_date:
            query += " AND Date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND Date <= ?"
            params.append(end_date)

        query += " ORDER BY Date DESC"

        return self.execute_query(query, tuple(params))

    def get_all_stock_data(self):
        """
        Return all stock price records.
        """

        query = """
            SELECT *
            FROM stock_prices
            ORDER BY
                Ticker,
                Date
        """

        return self.execute_query(query)

    def get_latest_data(self):
        """
        Return the latest available record for every ticker.
        """

        query = """
        SELECT sp1.*
        FROM stock_prices sp1
        INNER JOIN (
            SELECT
                Ticker,
                MAX(Date) AS LatestDate
            FROM stock_prices
            GROUP BY Ticker
        ) sp2
        ON sp1.Ticker = sp2.Ticker
        AND sp1.Date = sp2.LatestDate
        """

        return self.execute_query(query)

    def get_available_tickers(self):
        """
        Return all available tickers.
        """

        query = """
            SELECT DISTINCT Ticker
            FROM stock_prices
            ORDER BY Ticker
        """

        df = self.execute_query(query)

        if df.empty:
            return []

        return df["Ticker"].tolist()

    def get_date_range(self):
        """
        Return earliest and latest dates
        in the database.
        """

        query = """
            SELECT
                MIN(Date) AS Start_Date,
                MAX(Date) AS End_Date
            FROM stock_prices
        """

        return self.execute_query(query)

    def get_last_database_update(self):
        """
        Returns the most recent Processing_Date
        from the historical database.
        """

        query = """
            SELECT MAX(Processing_Date) AS LastUpdate
            FROM stock_prices
        """

        try:
            result = self.execute_query(query)

            if result.empty:
                return None

            return result.iloc[0]["LastUpdate"]

        except Exception:

            logger.exception(
                "Failed to retrieve last database update."
            )

            return None

    def get_record_count(self):
        """
        Return total number of records.
        """

        query = """
            SELECT COUNT(*) AS Total
            FROM stock_prices
        """

        df = self.execute_query(query)

        return int(df.iloc[0]["Total"])

    def get_ticker_count(self):
        """
        Return number of unique stocks.
        """

        query = """
            SELECT COUNT(DISTINCT Ticker) AS Total
            FROM stock_prices
        """

        df = self.execute_query(query)

        return int(df.iloc[0]["Total"])

    def get_latest_prices(self):
        """Get latest prices for all tickers"""

        query = '''
        SELECT sp1.*
        FROM stock_prices sp1
        INNER JOIN (
            SELECT Ticker, MAX(Date) as LatestDate
            FROM stock_prices
            GROUP BY Ticker
        ) sp2
        ON sp1.Ticker = sp2.Ticker
        AND sp1.Date = sp2.LatestDate
        ORDER BY sp1.Ticker
        '''

        return self.execute_query(query)

    def save_prediction(self, prediction_data: dict):
        """Save prediction to database"""

        try:

            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                INSERT INTO predictions
                (
                    Ticker,
                    Prediction_Date,
                    Predicted_Close,
                    Confidence_Interval_Lower,
                    Confidence_Interval_Upper,
                    Model_Used,
                    Created_At
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prediction_data['ticker'],
                    prediction_data['prediction_date'],
                    prediction_data['predicted_close'],
                    prediction_data.get('ci_lower'),
                    prediction_data.get('ci_upper'),
                    prediction_data.get('model_used', DEFAULT_MODEL),
                    datetime.now().isoformat()
                ))

                conn.commit()

                logger.info(
                    "Saved prediction for %s",
                    prediction_data["ticker"]
                )

        except Exception:

            logger.exception(
                "Failed to save prediction."
            )

            raise

    def _ensure_directory(self, folder_path: str):
        """Ensure directory exists before saving files"""
        os.makedirs(folder_path, exist_ok=True)

    def _validate_export_data(self, df):
        """Validate data before exporting reports"""

        if df is None or df.empty:
            logger.error(
                "Export failed: DataFrame is empty"
            )
            raise ValueError("No data available for export")

        required_columns = [
            'Ticker',
            'Close',
            'Volume'
        ]

        missing = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing:
            logger.error(
                "Missing required columns: %s",
                missing
            )
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        return True

    def _generate_timestamp(self):
        """Generate timestamp for unique filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def export_csv_report(self):
        """
        Export latest stock data to CSV
        with validation, logging and timestamps.
        """

        try:
            self._ensure_directory(REPORTS_PATH)

            df = self.get_latest_prices()

            self._validate_export_data(df)

            timestamp = self._generate_timestamp()

            output_path = (
                f"{REPORTS_PATH}/"
                f"consolidated_report_{timestamp}.csv"
            )

            df.to_csv(
                output_path,
                index=False
            )

            logger.info(
                "CSV report exported to %s",
                output_path
            )

            return output_path

        except Exception:

            logger.exception(
                "CSV export failed"
            )

            raise

    def export_excel_report(self):
        """
        Export latest stock data to Excel
        with validation, logging and timestamps.
        """

        try:
            self._ensure_directory(REPORTS_PATH)

            df = self.get_latest_prices()

            self._validate_export_data(df)

            timestamp = self._generate_timestamp()

            output_path = (
                f"{REPORTS_PATH}/"
                f"analysis_report_{timestamp}.xlsx"
            )

            df.to_excel(
                output_path,
                index=False
            )

            logger.info(
                "Excel report exported to %s",
                output_path
            )

            return output_path

        except Exception:

            logger.exception(
                "Excel export failed"
            )

            raise
                

    def insert_dataframe(
        self,
        table_name: str,
        df: pd.DataFrame,
        ignore_duplicates: bool = True
    ):
        """
        Insert a DataFrame into the specified table.
        """

        if df.empty:
            return 0
        
        try:
            with self.get_connection() as conn:

                cursor = conn.cursor()

                columns = ",".join(df.columns)

                placeholders = ",".join(
                    ["?"] * len(df.columns)
                )

                command = (
                    "INSERT OR IGNORE"
                    if ignore_duplicates
                    else
                    "INSERT"
                )

                sql = f"""
                    {command} INTO {table_name}
                    ({columns})
                    VALUES ({placeholders})
                """

                records = list(
                    df.itertuples(
                        index=False,
                        name=None
                    )
                )

                cursor.executemany(sql, records)

                logger.info(
                    "Inserted %d rows into %s.",
                    cursor.rowcount,
                    table_name
                )

                return cursor.rowcount
            
        except Exception:

            logger.exception(
                "Failed to insert rows into %s.",
                table_name
            )

            raise