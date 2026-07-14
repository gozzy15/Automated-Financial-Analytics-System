import pandas as pd

class DataService:
    """
    Responsible for loading stock data
    for one or more tickers.
    """

    def __init__(self, stock_repository):
        self.stock_repository = stock_repository

    def get_connection(self):
        return self.stock_repository.get_connection()

    def load_data(
        self,
        tickers: list[str],
        start_date: str | None,
        end_date: str | None
    ):
        """
        Load stock data for the selected tickers.

        Returns
        -------
        tuple
            (
                dictionary of ticker -> DataFrame,
                combined DataFrame
            )
        """

        all_data = {}

        combined_data = []

        if not tickers:

            return all_data, pd.DataFrame()

        for ticker in tickers:

            df = self.stock_repository.get_stock_data(
                ticker,
                start_date,
                end_date
            )

            if df.empty:
                continue

            all_data[ticker] = df

            df_copy = df.copy()

            df_copy["Ticker"] = ticker

            combined_data.append(df_copy)

        if combined_data:

            combined_df = pd.concat(
                combined_data,
                ignore_index=True
            )

        else:

            combined_df = pd.DataFrame()

        return all_data, combined_df
    
    def get_stock_data(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None
    ):
        """
        Return stock data for a single ticker.
        """

        return self.stock_repository.get_stock_data(
            ticker,
            start_date,
            end_date
        )

    def get_latest_data(self):
        """
        Get latest market prices.
        """

        return self.stock_repository.get_latest_data()

    def get_all_tickers(self):
        """
        Return every available ticker.
        """
        return self.stock_repository.get_all_tickers()