#!/usr/bin/env python3
"""Get live/real-time market data"""
import sys
import os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from financial_scraper import FinancialScraper
from datetime import datetime
import json

def main():
    print("=" * 60)
    print("📈 LIVE MARKET DATA DASHBOARD")
    print("=" * 60)

    try:
        scraper = FinancialScraper()
        current_time = datetime.now()

        # Get market status
        print("\n🏛️  MARKET STATUS:")
        market_status = scraper.get_market_status()
        for key, value in market_status.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")

        # Get live quotes
        print("\n💰 LIVE QUOTES:")
        realtime_data = scraper.get_realtime_tickers_data()

        for ticker, data in realtime_data.items():
            if 'error' not in data:
                print(f"\n📌 {ticker}")
                print(f"     Price: ${data.get('close', 0):.2f}")
                print(f"     Volume: {data.get('volume', 0):,}")
                print(f"     Last Updated: {data.get('last_updated', 'N/A')}")
            else:
                print(f"\n   {ticker}: {data['error']}")

        # Get detailed live quote for first ticker
        print("\n📊 DETAILED QUOTE (AAPL):")
        live_quote = scraper.get_live_quote('AAPL')
        if live_quote:
            print(f"   Current: ${live_quote.get('current_price', 0):.2f}")
            print(f"   Change: {live_quote.get('change', 0):.2f} ({live_quote.get('change_percent', 0):.2f}%)")
            print(f"   Day Range: ${live_quote.get('day_low', 0):.2f} - ${live_quote.get('day_high', 0):.2f}")
            print(f"   Volume: {live_quote.get('volume', 0):,} (Avg: {live_quote.get('avg_volume', 0):,})")
            print(f"   Market Cap: ${live_quote.get('market_cap', 0):,.0f}")

        # Get intraday data
        print("\n📈 INTRADAY DATA (AAPL last 5 intervals):")
        intraday = scraper.get_intraday_data('AAPL', period="1d", interval="15m")
        if not intraday.empty:
            print(intraday[['Open', 'High', 'Low', 'Close', 'Volume']].tail().to_string())
        else:
            print("   No intraday data available")

        print("\n" + "=" * 60)
        print("✅ Live data retrieved successfully!")
        print(f"Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Save to file
        output = {
            'timestamp': current_time.isoformat(),
            'market_status': market_status,
            'quotes': realtime_data,
            'detailed_quote': live_quote
        }

        os.makedirs('data/live', exist_ok=True)
        filename = f"data/live/market_data_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(f"\n💾 Data saved to: {filename}")

    except Exception as exc:
        print(f"\n❌ Error: {exc}")


if __name__ == "__main__":
    main()  # Call the main function if the script is run directly