class StockRepository:

    def __init__(
        self,
        database_handler
    ):
        self.database_handler = database_handler

    def get_connection(self):
        return self.database_handler.get_connection()

    def get_stock_data(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None
    ):

        return self.database_handler.get_stock_data(
            ticker,
            start_date,
            end_date
        )
    
    def get_latest_data(self):
        """
        Return the latest record for each ticker.
        """
        return self.database_handler.get_latest_data()

    def get_all_tickers(self):
        """
        Return all available stock tickers.
        """
        return self.database_handler.get_available_tickers()