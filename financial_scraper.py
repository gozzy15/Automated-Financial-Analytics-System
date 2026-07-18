import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import json
from utils.logger import logger
from processing_pipeline import DataPipeline
from zoneinfo import ZoneInfo

class FinancialScraper:
    def __init__(self):
        self.tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META']
    
    def scrape_yahoo_finance(self, tickers: List[str] = None, period: str = "1y", interval: str = "1d") -> Dict:
        """Scrape financial data from Yahoo Finance"""
        if tickers is None:
            tickers = self.tickers
        
        data = {}

        logger.info(
            "Starting Yahoo Finance scrape for %d ticker(s).",
            len(tickers)
        )

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                
                # Get historical data
                hist = stock.history(period=period, interval=interval)
                
                # Get financials
                financials = stock.financials
                balance_sheet = stock.balance_sheet
                cashflow = stock.cashflow
                
                # Get info (includes live data)
                info = stock.info
                
                # Get live quote
                live_quote = self.get_live_quote(ticker)
                
                data[ticker] = {
                    'historical': hist,
                    'financials': financials,
                    'balance_sheet': balance_sheet,
                    'cashflow': cashflow,
                    'info': info,
                    'live_quote': live_quote,
                    'timestamp': datetime.now()
                }
                
                logger.info(
                    "Successfully scraped data for %s.",
                    ticker
                )
                
            except Exception:
                logger.exception(
                    "Failed to scrape data for %s.",
                    ticker
                )

        logger.info(
            "Yahoo Finance scrape completed."
        )
        
        return data
    
    def get_live_quote(self, ticker: str) -> Dict:
        """Get live market quote for a ticker"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get live quote using info
            info = stock.info
            
            live_data = {
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('open', 0),
                'day_high': info.get('dayHigh', 0),
                'day_low': info.get('dayLow', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'market_cap': info.get('marketCap', 0),
                'bid': info.get('bid', 0),
                'ask': info.get('ask', 0),
                'bid_size': info.get('bidSize', 0),
                'ask_size': info.get('askSize', 0),
                'last_update': datetime.now().isoformat(),
                'change': info.get('regularMarketChange', 0),
                'change_percent': info.get('regularMarketChangePercent', 0),
                'currency': info.get('currency', 'USD')
            }
            
            return live_data
            
        except Exception:
            logger.exception(
                "Failed to get live quote for %s.",
                ticker
            )
            return {}
    
    def get_intraday_data(self, ticker: str, period: str = "1d", interval: str = "5m") -> pd.DataFrame:
        """Get intraday/live data with minute intervals"""
        try:
            stock = yf.Ticker(ticker)
            
            # For intraday data, use shorter periods
            # Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m
            # Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            intraday = stock.history(period=period, interval=interval)
            
            if not intraday.empty:
                logger.info(
                    "Retrieved %d intraday intervals for %s.",
                    len(intraday),
                    ticker
                )
                return intraday
            else:
                logger.warning(
                    "No intraday data available for %s.",
                    ticker
                )
                return pd.DataFrame()
                
        except Exception:
            logger.exception(
                "Failed to retrieve intraday data for %s.",
                ticker
            )
            return pd.DataFrame()
    
    def get_realtime_tickers_data(
        self,
        tickers: List[str] = None
    ) -> Dict:
        """
        Retrieve live market data for one or more tickers.

        Uses the latest available intraday candle from Yahoo Finance.
        This approach is more stable than relying on fast_info.
        """

        if tickers is None:
            tickers = self.tickers

        realtime_data = {}

        logger.info(
            "Retrieving real-time data for %d ticker(s).",
            len(tickers)
        )

        for ticker in tickers:

            try:

                stock = yf.Ticker(ticker)

                history = stock.history(
                    period="1d",
                    interval="1m",
                    auto_adjust=False
                )

                if history.empty:

                    logger.warning(
                        "No live market data available for %s",
                        ticker
                    )

                    realtime_data[ticker] = {
                        "error": "No market data available."
                    }

                    continue

                latest = history.iloc[-1]

                previous_close = 0.0

                if len(history) > 1:
                    previous_close = float(history.iloc[-2]["Close"])

                realtime_data[ticker] = {

                    "timestamp": datetime.now().isoformat(),

                    "open": float(latest["Open"]),

                    "high": float(latest["High"]),

                    "low": float(latest["Low"]),

                    "close": float(latest["Close"]),

                    "volume": int(latest["Volume"]),

                    "previous_close": previous_close,

                    "last_updated": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                }

            except Exception:

                logger.exception(
                    "Unable to retrieve live quote for %s",
                    ticker
                )

                realtime_data[ticker] = {
                    "error": "Unable to retrieve market data."
                }

        return realtime_data
        
    
    def scrape_marketwatch(self):
        """Scrape market news and insights"""
        url = "https://www.marketwatch.com/latest-news"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        for article in soup.find_all('div', class_='article__content', limit=10):
            title = article.find('h3', class_='article__headline')
            summary = article.find('p', class_='article__summary')
            
            if title and summary:
                articles.append({
                    'title': title.text.strip(),
                    'summary': summary.text.strip(),
                    'timestamp': datetime.now()
                })
        
        return articles
    
    def save_to_files(self, data: Dict, path: str):
        """Save scraped data to CSV and JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save each ticker's data
        for ticker, ticker_data in data.items():
            # Save historical data
            if 'historical' in ticker_data and not ticker_data['historical'].empty:
                hist_path = f"{path}/{ticker}_historical.csv"
                ticker_data['historical'].to_csv(hist_path)
            
            # Save financials
            if 'financials' in ticker_data and not ticker_data['financials'].empty:
                fin_path = f"{path}/{ticker}_financials_{timestamp}.csv"
                ticker_data['financials'].to_csv(fin_path)
            
            # Save live quote data
            if 'live_quote' in ticker_data and ticker_data['live_quote']:
                live_path = f"{path}/{ticker}_live_{timestamp}.json"
                with open(live_path, 'w') as f:
                    json.dump(ticker_data['live_quote'], f, indent=2)
        
        # Save metadata
        metadata = {
            'scrape_timestamp': timestamp,
            'tickers_scraped': list(data.keys()),
            'source': 'yahoo_finance'
        }
        
        with open(f"{path}/metadata_{timestamp}.json", 'w') as f:
            json.dump(metadata, f)
        
        return metadata
    
    def scheduled_scrape_job(self):
        """Scheduled weekly scraping job"""
        logger.info(
            "Scheduled market data update job."
        )
        
        try:
            # Scrape data
            data = self.scrape_yahoo_finance()
            
            # Save locally
            from system_config import RAW_DATA_PATH
            import os
            os.makedirs(RAW_DATA_PATH, exist_ok=True)
            
            metadata = self.save_to_files(data, RAW_DATA_PATH)
            pipeline = DataPipeline()
            logger.info(
                "Updating SQLite database..."
            )

            processed_files = pipeline.process_all_files()

            logger.info(
                "Database updated successfully. %d ticker(s) processed.",
                len(processed_files)
            )
            
            # Upload to Google Drive
            from cloud_manager import GoogleDriveHandler
            gdrive = GoogleDriveHandler()
            
            # Upload all CSV files
            for file in os.listdir(RAW_DATA_PATH):
                if file.endswith('.csv') or file.endswith('.json'):
                    file_path = os.path.join(RAW_DATA_PATH, file)
                    mime_type = 'text/csv' if file.endswith('.csv') else 'application/json'
                    gdrive.upload_file(file_path, file, mime_type)
            
            logger.info(
                "Scheduled market update started."
            )
            return metadata
        
        except Exception:
            logger.exception(
                "Scheduled market update failed."
            )
            raise
    
    def get_live_dashboard_data(self):
        """Get data specifically for live dashboard display"""
        logger.info(
            "Preparing live dashboard data."
        )
        
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'market_status': self.get_market_status(),
            'tickers': {},
            'news': self.scrape_marketwatch()[:5]  # Get top 5 news
        }
        
        # Get real-time data for all tickers
        realtime_data = self.get_realtime_tickers_data()
        
        for ticker in self.tickers:
            if ticker in realtime_data:
                dashboard_data['tickers'][ticker] = {
                    'realtime': realtime_data[ticker],
                    'quote': self.get_live_quote(ticker),
                    'intraday': self.get_intraday_data(ticker, period="1d", interval="15m").tail(20).to_dict('records')
                }
        
        return dashboard_data
    
    def get_market_status(self):
        """
        Determine whether the US stock market is currently open.

        Uses the official America/New_York timezone and also displays
        the equivalent local (West Africa Time) market opening time.

        Example:
            Wed Jul 15 • 09:30 AM ET / 02:30 PM WAT
        """

        # ----------------------------------------
        # Current Times
        # ----------------------------------------
        ny_tz = ZoneInfo("America/New_York")
        local_tz = ZoneInfo("Africa/Lagos")

        ny_time = datetime.now(ny_tz)
        local_time = ny_time.astimezone(local_tz)

        # ----------------------------------------
        # Today's Market Hours (New York Time)
        # ----------------------------------------
        market_open = ny_time.replace(
            hour=9,
            minute=30,
            second=0,
            microsecond=0
        )

        market_close = ny_time.replace(
            hour=16,
            minute=0,
            second=0,
            microsecond=0
        )

        # ----------------------------------------
        # Weekend Handling
        # ----------------------------------------
        if ny_time.weekday() >= 5:

            days_until_monday = 7 - ny_time.weekday()

            next_open = (
                ny_time + timedelta(days=days_until_monday)
            ).replace(
                hour=9,
                minute=30,
                second=0,
                microsecond=0
            )

        # ----------------------------------------
        # Market Currently Open
        # ----------------------------------------
        elif market_open <= ny_time < market_close:

            return {
                "is_open": True,
                "status": "OPEN",
                "hours": "9:30 AM – 4:00 PM ET",
                "current_time": (
                    f"{ny_time.strftime('%Y-%m-%d %I:%M:%S %p ET')} / "
                    f"{local_time.strftime('%I:%M:%S %p WAT')}"
                )
            }

        # ----------------------------------------
        # Before Market Opens Today
        # ----------------------------------------
        elif ny_time < market_open:

            next_open = market_open

        # ----------------------------------------
        # After Market Closes Today
        # ----------------------------------------
        else:

            next_open = market_open + timedelta(days=1)

            while next_open.weekday() >= 5:
                next_open += timedelta(days=1)

        # ----------------------------------------
        # Convert Next Open to Local Time
        # ----------------------------------------
        next_open_local = next_open.astimezone(local_tz)

        return {
            "is_open": False,
            "status": (
                "CLOSED (Weekend)"
                if ny_time.weekday() >= 5
                else "CLOSED"
            ),
            "next_open": (
                f"{next_open.strftime('%a %b %d • %I:%M %p ET')}"
                f"\n({next_open_local.strftime('%I:%M %p %Z')})"
            ),
            "current_time": (
                f"{ny_time.strftime('%Y-%m-%d %I:%M:%S %p ET')}"
                f"\n({local_time.strftime('%I:%M:%S %p %Z')})"
            )
        }