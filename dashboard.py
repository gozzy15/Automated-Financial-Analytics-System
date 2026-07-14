"""
Dash Dashboard for Financial Analytics
Alternative to Streamlit with more customization options
"""
import dash
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
from system_config import DASH_DEBUG, DASH_PORT
from financial_scraper import FinancialScraper
import warnings
warnings.filterwarnings('ignore')
from utils.logger import logger
from services.data_service import DataService
from services.analytics_service import AnalyticsService
from database_manager import DatabaseHandler
from repositories.stock_repository import StockRepository
from layout import create_layout
from callbacks.dashboard_callbacks import register_dashboard_callbacks

database_handler = DatabaseHandler()

stock_repository = StockRepository(database_handler)

data_service = DataService(stock_repository)

analytics_service = AnalyticsService(data_service)

logger.info("Dashboard application starting...")


# Initialize Dash app with Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

# Set app title
app.title = "Financial Analytics Dashboard"

# Register callbacks
register_dashboard_callbacks(
    app,
    data_service,
    analytics_service
)

# Database connection
DB_PATH = database_handler.db_path

# Initialize data
tickers = stock_repository.get_all_tickers()
latest_data = stock_repository.get_latest_data()
overall_metrics, ticker_metrics = analytics_service.calculate_metrics()

# Define app layout
app.layout = create_layout(
    tickers,
    latest_data,
    overall_metrics,
    ticker_metrics
)


# Run the app
if __name__ == '__main__':
    app.run(
            port=DASH_PORT,
            debug=DASH_DEBUG
        )