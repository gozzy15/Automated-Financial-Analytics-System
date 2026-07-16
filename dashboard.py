"""
Dash Dashboard for Financial Analytics
Alternative to Streamlit with more customization options
"""
import dash
from dash import html
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
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1"
        }
    ],
    suppress_callback_exceptions=True
)


# Expose Flask server for deployment (Gunicorn)
server = app.server

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

try:

    logger.info("Loading dashboard data...")

    tickers = stock_repository.get_all_tickers()
    latest_data = stock_repository.get_latest_data()

    overall_metrics, ticker_metrics = (
        analytics_service.calculate_metrics()
    )

    app.layout = create_layout(
        tickers,
        latest_data,
        overall_metrics,
        ticker_metrics
    )

    logger.info("Dashboard loaded successfully.")

except Exception:

    logger.exception("Dashboard failed to initialize.")

    app.layout = dbc.Container(

        [

            html.Br(),

            dbc.Alert(

                [

                    html.H3("Dashboard Initialization Failed"),

                    html.Hr(),

                    html.P(
                        "The dashboard could not load because the "
                        "financial database is unavailable or has not "
                        "been populated yet."
                    ),

                    html.P(
                        "Please run the data pipeline first, then "
                        "restart the dashboard."
                    ),

                ],

                color="danger"

            )

        ],

        fluid=True

    )


# Run the app
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=DASH_PORT,
        debug=DASH_DEBUG
    )