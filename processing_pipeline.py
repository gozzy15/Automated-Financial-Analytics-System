import pandas as pd
from datetime import datetime
from database_manager import DatabaseHandler
import os
from system_config import RAW_DATA_PATH, DB_PATH, PROCESSED_DATA_PATH
from utils.logger import logger

class DataPipeline:
    def __init__(self):
        self.raw_path = RAW_DATA_PATH
        self.clean_path = PROCESSED_DATA_PATH
        self.database = DatabaseHandler()
        self.db_path = DB_PATH

        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(self.clean_path, exist_ok=True)

    # =========================
    # DATABASE RESET (manual use only)
    # =========================
    def reset_database(self):
        try:
            with self.database.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("DROP TABLE IF EXISTS stock_prices")
                cursor.execute("DROP TABLE IF EXISTS predictions")
                cursor.execute("DROP TABLE IF EXISTS financial_metrics")

                logger.info("Database reset completed.")

        except Exception:
            logger.exception(
                "Failed to reset database."
            )
            raise

    # =========================
    # TRANSFORM STEP
    # =========================
    def transform_data(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:

        df_clean = df.copy()

        numeric_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        # --- Convert numeric columns safely ---
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(
                    df_clean[col],
                    errors="coerce"
                )

        # --- Clean Date safely ---
        if 'Date' in df_clean.columns:
            df_clean['Date'] = pd.to_datetime(
                df_clean['Date'],
                utc=True,
                errors='coerce'
            ).dt.strftime('%Y-%m-%d')

        # --- Forward fill Close ---
        if 'Close' in df_clean.columns:
            df_clean['Close'] = df_clean['Close'].ffill()

            # Returns
            df_clean['Daily_Return'] = df_clean['Close'].pct_change()
            df_clean['Cumulative_Return'] = (1 + df_clean['Daily_Return']).cumprod() - 1

            # Indicators
            df_clean['SMA_20'] = df_clean['Close'].rolling(20).mean()
            df_clean['SMA_50'] = df_clean['Close'].rolling(50).mean()

            delta = df_clean['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()

            rs = gain / loss
            df_clean['RSI'] = 100 - (100 / (1 + rs))

        # --- Metadata ---
        df_clean['Ticker'] = ticker
        df_clean['Processing_Date'] = datetime.now().isoformat()

        # --- Remove unwanted columns safely ---
        df_clean = df_clean.drop(
            columns=['Dividends', 'Stock Splits'],
            errors='ignore'
        )

        # --- Only drop truly critical missing values ---
        df_clean = df_clean.dropna(subset=['Date', 'Close'])

        # --- Remove duplicates based on Date and Ticker ---
        df_clean = df_clean.drop_duplicates(
            subset=["Date", "Ticker"]
        )

        return df_clean

        

    # =========================
    # LOAD STEP
    # =========================
    def load_to_database(
        self,
        df: pd.DataFrame,
        table_name: str
    ):
        """
        Load cleaned data into the database.
        """

        inserted = self.database.insert_dataframe(
            table_name,
            df
        )

        logger.info(
            "Inserted %s rows into %s.",
            inserted,
            table_name
        )

    # =========================
    # FILE SORT HELPERS
    # =========================
    def _extract_timestamp(self, filename):
        """
        Extract full timestamp from filenames like:

        AAPL_historical_20260622_155144.csv

        Returns:
            20260622155144
        """

        try:
            name = filename.replace(".csv", "")
            parts = name.split("_")

            date_part = parts[-2]
            time_part = parts[-1]

            return date_part + time_part

        except Exception:

            logger.warning(
                "Unable to extract timestamp from %s",
                filename
            )

            return ""
            

    # =========================
    # PROCESS FILES (LATEST ONLY PER TICKER)
    # =========================
    def process_all_files(self):

        processed_files = []
        ticker_files: dict[str, list[str]] = {}

        # --- Group files by ticker ---
        for file in os.listdir(self.raw_path):
            if file.endswith('.csv') and 'historical' in file:

                ticker = file.split('_')[0]

                if ticker not in ticker_files:
                    ticker_files[ticker] = []

                ticker_files[ticker].append(file)

        # --- Process ONLY latest file per ticker ---
        for ticker, files in ticker_files.items():

            # sort using timestamp (safe method)
            files.sort(key=self._extract_timestamp, reverse=True)
            latest_file = files[0]

            try:
                file_path = os.path.join(self.raw_path, latest_file)
                
                logger.info(
                    "Processing %s",
                    file_path
                )

                df = pd.read_csv(file_path)

                logger.info(
                    "%s rows loaded from %s",
                    len(df),
                    latest_file
                )

                logger.info(
                    "Date range: %s -> %s",
                    df["Date"].min(),
                    df["Date"].max()
                )

                df_clean = self.transform_data(df, ticker)

                logger.info(
                    "Rows after transform for %s: %s",
                    ticker,
                    len(df_clean)
                )

                logger.info(
                    "Date range: %s -> %s",
                    df["Date"].min(),
                    df["Date"].max()
                )

                # save cleaned version
                clean_file = f"clean_{latest_file}"
                clean_path = os.path.join(self.clean_path, clean_file)
                df_clean.to_csv(clean_path, index=False)

                # load into DB
                self.load_to_database(df_clean, 'stock_prices')

                processed_files.append(latest_file)

                logger.info(
                    "Finished processing %s",
                    ticker
                )

            except Exception:

                logger.exception(
                    "Failed processing %s",
                    latest_file
                )

        return processed_files

    # =========================
    # PIPELINE RUNNER
    # =========================
    def run_pipeline(self, gdrive_handler):

        logger.info(
            "Starting ETL pipeline."
        )

        logger.info(
            "Downloading raw files."
        )
        try:
            #gdrive_handler = GoogleDriveHandler()
            files = gdrive_handler.list_files()

            for file in files:
                if file['name'].endswith('.csv'):
                    dest_path = os.path.join(self.raw_path, file['name'])
                    gdrive_handler.download_file(file['id'], dest_path)

            logger.info(
                "Transforming and loading data."
            )
            processed = self.process_all_files()

            logger.info(
                "Uploading cleaned data."
            )
            for file in os.listdir(self.clean_path):
                if file.endswith('.csv'):
                    path = os.path.join(self.clean_path, file)
                    gdrive_handler.upload_file(path, file, 'text/csv')

            logger.info(
                "ETL pipeline completed. %s files processed.",
                len(processed)
            )

            return processed
        except Exception:
            logger.exception(
                "ETL pipeline failed."
            )

            raise