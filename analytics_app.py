import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import schedule
import time
import threading
from financial_scraper import FinancialScraper
from database_manager import DatabaseHandler
from prediction_engine import FinancialPredictor
from email_reporter import EmailReporter
from utils.logger import logger
import requests
from utils.live_clock import display_live_clock

# Page configuration
st.set_page_config(
    page_title="Financial Analytics System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}

class FinancialDashboard:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        self.predictor = FinancialPredictor()
        self.email_reporter = EmailReporter()
        self.scraper = FinancialScraper()

    def format_database_update(self):
        """
        Format the last database refresh time
        into a user-friendly string.
        """

        last_update = self.db_handler.get_last_database_update()

        if not last_update:
            return "No data available"

        try:
            # Processing_Date was stored as ISO format
            update_time = datetime.fromisoformat(last_update)

            # Treat stored timestamp as local (WAT) if it has no timezone
            if update_time.tzinfo is None:
                update_time = update_time.replace(
                    tzinfo=ZoneInfo("Africa/Lagos")
                )

            now = datetime.now(ZoneInfo("Africa/Lagos"))

            if update_time.date() == now.date():

                return (
                    f"Today • "
                    f"{update_time.strftime('%I:%M %p')} WAT"
                )

            elif (now.date() - update_time.date()).days == 1:

                return (
                    f"Yesterday • "
                    f"{update_time.strftime('%I:%M %p')} WAT"
                )

            else:

                return update_time.strftime(
                    "%a %b %d • %I:%M %p WAT"
                )

        except Exception:

            logger.exception(
                "Unable to format database update time."
            )

            return str(last_update)

    def get_database_status(self):
        """
        Returns a status icon and a formatted
        database refresh time.
        """

        last_update = self.db_handler.get_last_database_update()

        if not last_update:
            return "🔴", "No data available"

        try:
            update_time = datetime.fromisoformat(last_update)

            if update_time.tzinfo is None:
                update_time = update_time.replace(
                    tzinfo=ZoneInfo("Africa/Lagos")
                )

            now = datetime.now(ZoneInfo("Africa/Lagos"))

            days_old = (now.date() - update_time.date()).days

            if days_old == 0:

                status = "🟢"

            elif days_old == 1:

                status = "🟡"

            else:

                status = "🔴"

            return status, self.format_database_update()

        except Exception:

            logger.exception(
                "Unable to determine database status."
            )

            return "🔴", "Unknown"
    
    def display_header(self):
        """Display dashboard header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.title("📊 Financial Analytics Dashboard")
            st.markdown("---")
    
    def display_sidebar(self):
        """Display sidebar with filters and controls"""
        with st.sidebar:
            st.header("⚙️ Controls")
            
            # Date range selector
            st.subheader("Date Range")
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start", datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End", datetime.now())
            
            # Ticker selector
            st.subheader("Ticker Selection")
            tickers = self.db_handler.execute_query(
                "SELECT DISTINCT Ticker FROM stock_prices ORDER BY Ticker"
            )['Ticker'].tolist()
            
            selected_tickers = st.multiselect(
                "Select Tickers",
                tickers,
                default=tickers[:3] if tickers else []
            )
            
            # Analysis type
            st.subheader("Analysis Type")
            analysis_type = st.selectbox(
                "Select Analysis",
                ["Price Trends", "Technical Indicators", "Predictive Analytics", "Portfolio Analysis"]
            )
            
            # Auto-refresh
            st.subheader("Auto-Refresh")
            auto_refresh = st.checkbox("Enable Auto-Refresh", value=False)
            if auto_refresh:
                refresh_interval = st.slider("Refresh Interval (minutes)", 1, 60, 5)
            
            # Action buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            #with col1:
                #if st.button("🔄", help="Refresh Data", width='stretch'):
                    #self.refresh_data()"""
            
            with col1:
                if st.button("📧", help="Send Weekly Report", width='stretch'):
                    self.send_report()
            
            with col2:
                if st.button("🤖", help="Run Predictions", width='stretch'):
                    self.run_predictions()
            
            # Link to Advanced Dashboard
            st.markdown("---")
            
            # Check Streamlit version for optimal method
            try:
                # Try modern link_button (Streamlit 1.25+)
                st.link_button(
                    "🌐 Open Advanced Dashboard",
                    "http://localhost:8050",
                    width='stretch',
                    help="Opens the advanced Dash dashboard in a new tab"
                )
            except Exception:
                # Fallback for older Streamlit versions
                if st.button("🌐 Open Advanced Dashboard", width='stretch'):
                    # JavaScript to open in new tab
                    js = """
                    <script>
                    window.open('http://localhost:8050', '_blank').focus();
                    </script>
                    """
                    st.components.v1.html(js, height=0)
            
            # Dashboard status indicator
            st.markdown("---")
            with st.expander("📊 Dashboard Status"):

                # Check if Dash is running
                try:
                    response = requests.get("http://localhost:8050", timeout=2)
                    if response.status_code == 200:
                        st.success("✅ Dash dashboard is running")
                        st.markdown("**Access:** http://localhost:8050")
                    else:
                        st.warning("⚠️ Dash dashboard might not be running")
                except Exception:
                    st.error("❌ Dash dashboard is not running")
                    st.markdown("""
                    To start the advanced dashboard:
                    ```
                    python dashboard.py
                    ```
                    """)

            st.markdown("---")

            update_info = self.format_database_update()

            st.markdown(
                "**📅 Last Database Refresh**"
            )

            st.caption(update_info)

            from system_config import APP_NAME, APP_VERSION, AUTHOR, LINK

            st.markdown("---")

            st.markdown(
                f"""
                <div style="text-align:center; font-size:13px; color:#6c757d;">
                    <strong>{APP_NAME}</strong><br>
                    {APP_VERSION}<br>
                    Built by <strong>{AUTHOR}</strong><br>
                    <a href={LINK} target="_blank">
                        View Source on GitHub
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'tickers': selected_tickers,
                'analysis_type': analysis_type,
                'auto_refresh': auto_refresh
            }
    
    """def refresh_data(self):
        Refresh data from Google Drive
        with st.spinner("Refreshing data..."):
            try:
                gdrive = GoogleDriveHandler()
                pipeline = DataPipeline()
                pipeline.run_pipeline(gdrive)
                st.success("Data refreshed successfully!")
                st.session_state.data_loaded = True
            except Exception as e:
                st.error(f"Error refreshing data: {e}")"""
    
    def send_report(self):
        """Send weekly report"""
        with st.spinner("Generating and sending report..."):
            try:
                success = self.email_reporter.generate_weekly_report()
                if success:
                    st.success("Weekly report sent successfully!")
                else:
                    st.error("Failed to send report")

            except Exception:
                logger.exception(
                    "Failed to generate weekly report."
                )
                st.error(
                    "Failed to send report."
                )
    
    def run_predictions(self):
        """Run ML predictions"""
        with st.spinner("Running predictions..."):
            try:
                params = st.session_state.get('sidebar_params', {})
                tickers = params.get('tickers', [])
                
                logger.info(
                    "Running predictions for %d tickers.",
                    len(tickers)
                )

                for ticker in tickers:
                    prediction = self.predictor.predict_future(ticker)
                    if prediction:
                        st.session_state.predictions[ticker] = prediction
                
                st.success(f"Predictions completed for {len(tickers)} tickers!")
                
                logger.info(
                    "Prediction completed successfully."
                )

            except Exception:
                logger.exception(
                    "Prediction failed."
                )

                st.error(
                    "Error running predictions."
                )
    
    def display_metrics(self, tickers):
        """Display key metrics using get_latest_prices()"""
        st.subheader("📊 Latest Market Snapshot")
        
        try:
            # Get latest prices for all tickers at once
            latest_prices = self.db_handler.get_latest_prices()
            
            if latest_prices.empty:
                st.warning("⚠️ No data available")
                return
            
            # Filter for selected tickers
            selected_data = latest_prices[latest_prices['Ticker'].isin(tickers)]
            
            # Create columns
            cols = st.columns(min(4, len(tickers)))
            
            for idx, ticker in enumerate(tickers[:4]):
                with cols[idx]:
                    # Find data for this ticker
                    ticker_data = selected_data[selected_data['Ticker'] == ticker]
                    
                    if not ticker_data.empty:
                        row = ticker_data.iloc[0]
                        price = row.get('Close', 0)
                        returns = row.get('Daily_Return', 0) * 100
                        
                        st.metric(
                            label=ticker,
                            value=f"${price:.2f}",
                            delta=f"{returns:+.2f}%"
                        )
                        
                        # Show additional info on hover
                        with st.expander("Details", expanded=False):
                            st.write(f"**Date:** {row.get('Date', 'N/A')}")
                            st.write(f"**Volume:** {row.get('Volume', 0):,}")
                            if 'RSI' in row:
                                st.write(f"**RSI:** {row['RSI']:.1f}")
                    else:
                        st.metric(label=ticker, value="N/A", delta="0%")
                        
        except Exception as e:
            st.error(f"Error loading metrics: {str(e)[:100]}")
            
            # Fallback to simple display
            cols = st.columns(min(4, len(tickers)))
            for idx, ticker in enumerate(tickers[:4]):
                with cols[idx]:
                    st.metric(label=ticker, value="Error", delta="0%")
    
    def display_price_chart(self, tickers, start_date, end_date):
        """Display price chart"""
        st.subheader("💹 Price Trends")
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Price Movement', 'Volume'),
            row_heights=[0.7, 0.3]
        )
        
        for ticker in tickers:
            data = self.db_handler.get_stock_data(
                ticker,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if not data.empty:
                # Price chart
                fig.add_trace(
                    go.Candlestick(
                        x=data['Date'],
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name=ticker,
                        showlegend=True
                    ),
                    row=1, col=1
                )
                
                # Volume chart
                colors = ['red' if row['Close'] < row['Open'] else 'green' 
                         for _, row in data.iterrows()]
                
                fig.add_trace(
                    go.Bar(
                        x=data['Date'],
                        y=data['Volume'],
                        name=f"{ticker} Volume",
                        marker_color=colors,
                        showlegend=False
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            height=600,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def display_technical_indicators(self, ticker, start_date, end_date):
        """Display technical indicators"""
        st.subheader(f"📊 Technical Indicators - {ticker}")
        
        data = self.db_handler.get_stock_data(
            ticker,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if data.empty:
            st.warning(f"No data available for {ticker}")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price with Moving Averages', 'RSI', 'Daily Returns'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price with MAs
        fig.add_trace(
            go.Scatter(x=data['Date'], y=data['Close'], name=f'Close ({ticker})', line=dict(color='blue')),
            row=1, col=1
        )
        
        if 'SMA_20' in data.columns:
            fig.add_trace(
                go.Scatter(x=data['Date'], y=data['SMA_20'], name='SMA 20', line=dict(color='orange', dash='dash')),
                row=1, col=1
            )
        
        if 'SMA_50' in data.columns:
            fig.add_trace(
                go.Scatter(x=data['Date'], y=data['SMA_50'], name='SMA 50', line=dict(color='red', dash='dot')),
                row=1, col=1
            )
        
        # RSI
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(x=data['Date'], y=data['RSI'], name='RSI', line=dict(color='purple')),
                row=2, col=1
            )
            
            # Add RSI bands
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Daily Returns
        if 'Daily_Return' in data.columns:
            colors = ['green' if x >= 0 else 'red' for x in data['Daily_Return']]
            fig.add_trace(
                go.Bar(x=data['Date'], y=data['Daily_Return']*100, name='Daily Return %', 
                      marker_color=colors),
                row=3, col=1
            )
        
        fig.update_layout(height=800, showlegend=True, template='plotly_white')
        st.plotly_chart(fig, width='stretch')
    
    def display_predictions(self):
        """Display ML predictions"""
        st.subheader("🔮 Predictive Analytics")
        
        if not st.session_state.predictions:
            st.info("Run predictions using the sidebar button first.")
            return
        
        # Display predictions in columns
        cols = st.columns(min(3, len(st.session_state.predictions)))
        
        for idx, (ticker, prediction) in enumerate(st.session_state.predictions.items()):
            with cols[idx % len(cols)]:
                st.markdown(f"### {ticker}")
                
                # Prediction card
                current_price = prediction['current_price']
                predicted_price = prediction['predicted_close']
                expected_return = prediction['expected_return']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current", f"${current_price:.2f}")
                with col2:
                    st.metric(
                        "Predicted (1 week)", 
                        f"${predicted_price:.2f}",
                        f"{expected_return:.2f}%"
                    )
                
                # Confidence interval
                st.progress(min(95, abs(int(expected_return)) + 50))
                st.caption(f"Confidence: {prediction['ci_lower']:.2f} - {prediction['ci_upper']:.2f}")
                
                # Feature importance
                if 'feature_importance' in prediction:
                    with st.expander("Top Features"):
                        for feature in prediction['feature_importance'][:5]:
                            st.text(f"{feature['feature']}: {feature['importance']:.3f}")
    
    def display_data_table(self, tickers, start_date, end_date):
        """Display data table"""
        st.subheader("📋 Raw Data")
        
        all_data = []
        for ticker in tickers:
            data = self.db_handler.get_stock_data(
                ticker,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            all_data.append(data)
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            st.dataframe(
                combined_data,
                width='stretch',
                hide_index=True
            )
            
            # Download button
            csv = combined_data.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            
    def display_live_data(self, tickers):
        """Display live market data"""
        st.markdown(
            """
            <h2 style="
                text-align: center;
                margin-bottom: 20px;
                font-weight: bold;
            ">
                ⚡ Market Watch
            </h2>
            """,
            unsafe_allow_html=True
        )

        try:
            scraper = self.scraper

            # Get market status
            market_status = scraper.get_market_status()

            # -----------------------------------
            # Determine quote status
            # -----------------------------------

            if market_status["is_open"]:

                live_icon = "🟢"
                live_label = "Live Market"

            elif "Weekend" in market_status["status"]:

                live_icon = "⚫"
                live_label = "Weekend Close"

            else:

                live_icon = "🟡"
                live_label = "Last Market Close"

            # -------------------------
            # Data Freshness
            # -------------------------

            status_icon, database_update = self.get_database_status()

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "💰 Quote Feed",
                    live_label
                )

            with col2:

                st.metric(
                    "🗄 Database",
                    status_icon
                )

                st.caption(f"Updated: {database_update}")

            with col3:

                st.metric(
                    "🤖 Prediction Engine",
                    "READY"
                )

                st.caption("Using latest database")

            with col4:

                st.metric(
                    "📈 Market",
                    market_status["status"]
                )

                if market_status["is_open"]:

                    st.caption("Trading session active")

                else:

                    st.caption("Awaiting next session")

            st.divider()

            display_live_clock()
                 
            # Status indicator
            col1, col2 = st.columns(2)
            with col1:
                if market_status['is_open']:
                    st.markdown("**Market Status**")
                    st.success(f"✅ {market_status['status']}")
                else:
                    st.markdown("**Market Status**")
                    st.warning(f"⏸️ {market_status['status']}")
            
            with col2:
                if not market_status['is_open']:
                    st.markdown("**Next Market Open**")
                    st.info(market_status["next_open"])
            
            # Get live quotes
            st.subheader("💰 Live Quotes")
            realtime_data = scraper.get_realtime_tickers_data(tickers)
            
            # Display in columns
            cols = st.columns(len(tickers))
            for idx, ticker in enumerate(tickers):
                with cols[idx]:
                    if ticker in realtime_data and 'error' not in realtime_data[ticker]:
                        data = realtime_data[ticker]
                        
                        # Calculate change from open
                        change = 0

                        if (
                            "close" in data
                            and "previous_close" in data
                            and data["previous_close"] > 0
                        ):

                            change = (
                                (data["close"] - data["previous_close"])
                                / data["previous_close"]
                            ) * 100
                        
                        st.metric(
                            label=ticker,
                            value=f"${data.get('close', 0):.2f}",
                            delta=f"{change:+.2f}%"
                        )
                        
                        # Additional info in expander
                        with st.expander("Details"):
                            st.write(f"**Open:** ${data.get('open', 0):.2f}")
                            st.write(f"**High:** ${data.get('high', 0):.2f}")
                            st.write(f"**Low:** ${data.get('low', 0):.2f}")
                            st.write(f"**Volume:** {data.get('volume', 0):,}")
                            if 'last_updated' in data:
                                st.write(f"**Updated:** {data['last_updated']}")
                    else:
                        st.metric(label=ticker, value="N/A", delta="0%")
            
            # Auto-refresh option
            st.markdown("---")
            auto_refresh = st.checkbox("🔄 Auto-refresh live data", value=False)
            if auto_refresh:
                refresh_interval = st.select_slider(
                    "Refresh interval",
                    options=[5, 10, 15, 30, 60],
                    value=15,
                    format_func=lambda x: f"{x} seconds"
                )
                st.info(f"Live data will refresh every {refresh_interval} seconds")
                
                # Use Streamlit's built-in refresh
                time.sleep(refresh_interval)
                st.rerun()
            
        except Exception:
            logger.exception(
                "Failed to display live market data."
            )
            st.error(
                "Unable to load live market data."
            )
    
    def run_scheduler(self):
        """Run scheduled tasks in background"""
        scraper = self.scraper
        
        # Schedule weekly scraping
        schedule.every().monday.at("09:00").do(scraper.scheduled_scrape_job)
        
        # Schedule weekly reporting
        schedule.every().friday.at("17:00").do(self.email_reporter.generate_weekly_report)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run(self):
        """Main dashboard runner"""
        self.display_header()
        
        # Get sidebar parameters
        sidebar_params = self.display_sidebar()
        st.session_state.sidebar_params = sidebar_params
        
        # Extract parameters
        tickers = sidebar_params['tickers']
        start_date = sidebar_params['start_date']
        end_date = sidebar_params['end_date']
        analysis_type = sidebar_params['analysis_type']
        
        # Start scheduler in background thread

        # Scheduler disabled during cloud deployment

        # if "scheduler_started" not in st.session_state:
        #
        #     scheduler_thread = threading.Thread(
        #         target=self.run_scheduler,
        #         daemon=True
        #     )
        #
        #     scheduler_thread.start()
        #
        #     st.session_state.scheduler_started = True

        # Historical data updates will eventually be handled by
        # a dedicated scheduled job (Render Cron Job or GitHub
        # Actions), keeping the Streamlit app focused solely on
        # serving users.
        # =====================================================

        logger.info(
            "Background scheduler disabled (deployment mode)."
        )
        
        if not tickers:
            st.warning("Please select at least one ticker from the sidebar.")
            return
        
        # Display LIVE DATA FIRST
        self.display_live_data(tickers)
        
        # Display metrics
        self.display_metrics(tickers)
        
        # Main content based on analysis type
        if analysis_type == "Price Trends":
            self.display_price_chart(tickers, start_date, end_date)
            
        elif analysis_type == "Technical Indicators":
            selected_ticker = st.selectbox("Select Ticker for Technical Analysis", tickers)
            if selected_ticker:
                self.display_technical_indicators(selected_ticker, start_date, end_date)
                
        elif analysis_type == "Predictive Analytics":
            self.display_predictions()
            
        elif analysis_type == "Portfolio Analysis":
            st.subheader("📊 Portfolio Analysis")
            # Add portfolio analysis logic here
            st.info(
                "Portfolio Analysis is currently available in the advanced Dash dashboard."
                )
        
        # Always show data table at the bottom
        self.display_data_table(tickers, start_date, end_date)

def main():
    # Initialize dashboard
    logger.info(
        "Starting Streamlit dashboard."
    )
    dashboard = FinancialDashboard()
    
    # Run dashboard
    dashboard.run()

if __name__ == "__main__":
    main()