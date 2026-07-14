#!/usr/bin/env python3
"""Continuous live data stream"""
import time
from datetime import datetime
from financial_scraper import FinancialScraper
import json
import os

STREAM_FOLDER = "data/stream"

class LiveDataStream:
    def __init__(self, update_interval: int =30):  # seconds
        self.scraper = FinancialScraper()
        self.update_interval = update_interval
        self.market_closed_message_shown = False
        os.makedirs(STREAM_FOLDER, exist_ok=True)
    
    def start_stream(self):
        """Start continuous data stream"""
        print(
            f"🌊 Live data stream started at "
            f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        )
        print(f"📡 Streaming {len(self.scraper.tickers)} tickers")
        print(f"⏱️  Update interval: {self.update_interval} seconds")
        print("-" * 50)
        
        try:
            while True:

                # -----------------------------
                # Wait for the market to open
                # -----------------------------
                while True:
                    timestamp = datetime.now()
                    status = self.scraper.get_market_status()

                    if status["is_open"]:
                        self.market_closed_message_shown = False
                        print("\n✅ Market is now OPEN. Starting live stream...")
                        break

                    if not self.market_closed_message_shown:
                        print(f"\n🕐 {timestamp:%Y-%m-%d %H:%M:%S}")
                        #print(f"🏛️  Market: {status['status']}")
                        print(
                            f"⏸️ Market is now {status['status']}."
                        )
                        print(
                            f"🕒 Next open: {status['next_open']}"
                        )
                        print("\n📊 Last Available Market Data:\n")

                        data = self.scraper.get_realtime_tickers_data()

                        for ticker, ticker_data in data.items():
                            if "error" not in ticker_data:
                                price = ticker_data.get("close", 0)
                                volume = ticker_data.get("volume", 0)

                                print(
                                    f"   {ticker}: "
                                    f"${price:.2f} | 📊 {volume:,}"
                                )

                        
                        print("\n⏳ Waiting silently for the next OPEN...")

                        self.market_closed_message_shown = True

                    time.sleep(self.update_interval)

                # -----------------------------
                # Stream while market is open
                # -----------------------------
                while True:
                    timestamp = datetime.now()
                    status = self.scraper.get_market_status()

                    if not status["is_open"]:
                        print("\n🔔 Market has closed.")
                        break

                    print(f"\n🕐 {timestamp:%Y-%m-%d %H:%M:%S}")

                    data = self.scraper.get_realtime_tickers_data()

                    for ticker, ticker_data in data.items():
                        if "error" not in ticker_data:
                            price = ticker_data.get("close", 0)
                            volume = ticker_data.get("volume", 0)

                            print(
                                f"   {ticker}: "
                                f"${price:.2f} | 📊 {volume:,}"
                            )

                    self.save_snapshot(data, timestamp)

                    time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Live stream stopped by user")
    
    def save_snapshot(self, data, timestamp):
        """Save data snapshot"""
        try:
            snapshot = {
                'timestamp': timestamp.isoformat(),
                'data': data
            }
            
            filename = f"{STREAM_FOLDER}/snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(snapshot, f, indent=2)
            
            # Keep only last 100 files
            self.cleanup_old_files(STREAM_FOLDER, 100)

        except Exception as exc:
            print(f"⚠️ Failed to save snapshot: {exc}")
    
    def cleanup_old_files(self, directory, keep_count: int =100):
        """Keep only recent files"""
        files = [os.path.join(directory, f) for f in os.listdir(directory) 
                if f.startswith('snapshot_') and f.endswith('.json')]
        files.sort(key=os.path.getmtime)
        
        if len(files) > keep_count:
            for file_to_delete in files[:-keep_count]:
                try:
                    os.remove(file_to_delete)

                except OSError as exc:
                    print(
                        f"Could not delete "
                        f"{file_to_delete}: {exc}"
                    )

if __name__ == "__main__":
    stream = LiveDataStream(update_interval=30)  # Update every 30 seconds
    stream.start_stream()