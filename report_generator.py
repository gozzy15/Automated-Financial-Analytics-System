import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from database_manager import DatabaseHandler
from prediction_engine import FinancialPredictor


class ReportGenerator:
    """
    Generate professional HTML financial reports.
    """

    def __init__(self):
        self.db = DatabaseHandler()
        self.predictor = FinancialPredictor()

        self.clean_dir = "data/clean/final_dashboard"
        self.logs_dir = "logs"

        self.create_directories()
        self.setup_logging()

    def create_directories(self):
        """
        Create required directories if they do not exist.
        """

        os.makedirs(self.clean_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def setup_logging(self):
        """
        Configure logging.
        """

        log_file = os.path.join(
            self.logs_dir,
            "report_generator.log"
        )

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s"
        )

        logging.info("ReportGenerator initialized")

    def validate_data(self, df: pd.DataFrame):
        """
        Validate dataset before report generation.
        """

        if df is None:
            raise ValueError("DataFrame is None")

        if df.empty:
            raise ValueError("DataFrame is empty")

        required_columns = [
            "Ticker",
            "Close",
            "Volume",
            "Daily_Return"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        return True

    def generate_metrics(self, latest_prices: pd.DataFrame):
        """
        Generate executive summary metrics.
        """

        one_year_ago = (
            datetime.now() - timedelta(days=365)
        ).strftime("%Y-%m-%d")

        self.validate_data(latest_prices)

        total_tickers = latest_prices["Ticker"].nunique()

        avg_return = (
            latest_prices["Daily_Return"].mean() * 100
        )

        total_volume = (
            latest_prices["Volume"].sum()
        )

        data_points = 0

        for ticker in self.get_available_tickers():
            df = self.db.get_stock_data(
                ticker,
                start_date=one_year_ago
            )
            data_points += len(df)

        metrics = {
            "total_tickers_analyzed": total_tickers,
            "average_daily_return": round(avg_return, 2),
            "total_volume_traded": int(total_volume),
            "data_points_analyzed": data_points,
            "report_date": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        logging.info(
            f"Metrics generated for {total_tickers} tickers"
        )

        return metrics

    def get_available_tickers(self):
        """
        Retrieve available tickers from latest prices.
        """

        latest_prices = self.db.get_latest_prices()

        if latest_prices.empty:
            return []

        return latest_prices["Ticker"].unique().tolist()

    def generate_predictions(self, limit=10):
        """
        Generate trading signals and predictions.
        """

        predictions = []

        tickers = self.get_available_tickers()

        if not tickers:
            logging.warning(
                "No tickers available for prediction generation"
            )
            return predictions

        for ticker in tickers[:limit]:

            try:
                signal = (
                    self.predictor
                    .generate_trading_signals(ticker)
                )

                if signal:
                    predictions.append(signal)

                    logging.info(
                        f"Prediction generated for {ticker}"
                    )

            except Exception as e:

                logging.error(
                    f"Prediction failed for "
                    f"{ticker}: {e}"
                )

        return predictions

    def create_price_chart(self, tickers=None):
        """
        Create interactive price trend chart.
        """

        one_year_ago = (
            datetime.now() - timedelta(days=365)
        ).strftime("%Y-%m-%d")

        try:

            if tickers is None:
                tickers = self.get_available_tickers()[:5]

            combined_data = []

            for ticker in tickers:

                df = self.db.get_stock_data(
                    ticker, 
                    start_date = one_year_ago
                    )

                if not df.empty:

                    df_copy = df.copy()

                    df_copy["Ticker"] = ticker

                    combined_data.append(df_copy)

            if not combined_data:

                logging.warning(
                    "No data available for price chart"
                )

                return "<p>No price chart available.</p>"

            chart_df = pd.concat(
                combined_data,
                ignore_index=True
            )

            print(chart_df["Ticker"].unique())
            print(chart_df["Ticker"].value_counts())

            print(chart_df.head())
            print(chart_df.tail())
            print(chart_df.columns)

            fig = px.line(
                chart_df,
                x="Date",
                y="Close",
                color="Ticker",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                title="Price Trends"
            )

            print(len(fig.data))

            for trace in fig.data:
                print(trace.name)

            print(chart_df["Ticker"].dtype)

            fig.update_layout(
                template="plotly_white",
                height=500
            )

            logging.info(
                "Price chart created successfully"
            )

            return fig.to_html(
                full_html=False,
                include_plotlyjs="cdn"
            )

        except Exception as e:

            logging.error(
                f"Price chart creation failed: {e}"
            )

            return (
                "<p>Error generating "
                "price chart.</p>"
            )

    def create_volume_chart(self, tickers=None):
        """
        Create volume analysis chart.
        """

        one_year_ago = (
            datetime.now() - timedelta(days=365)
        ).strftime("%Y-%m-%d")

        try:

            if tickers is None:
                tickers = self.get_available_tickers()[:5]

            combined_data = []

            for ticker in tickers:

                df = self.db.get_stock_data(
                    ticker, 
                    start_date = one_year_ago
                    )

                if not df.empty:

                    df_copy = df.copy()

                    df_copy["Ticker"] = ticker

                    combined_data.append(df_copy)

            if not combined_data:

                logging.warning(
                    "No data available for volume chart"
                )

                return "<p>No volume chart available.</p>"

            chart_df = pd.concat(
                combined_data,
                ignore_index=True
            )

            fig = px.bar(
                chart_df,
                x="Date",
                y="Volume",
                color="Ticker",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                title="Volume Analysis"
            )

            fig.update_layout(
                template="plotly_white",
                height=500
            )

            logging.info(
                "Volume chart created successfully"
            )

            return fig.to_html(
                full_html=False,
                include_plotlyjs=False
            )

        except Exception as e:

            logging.error(
                f"Volume chart creation failed: {e}"
            )

            return (
                "<p>Error generating "
                "volume chart.</p>"
            )

    def create_returns_chart(self, tickers=None):
        """
        Create daily return comparison chart.
        """

        one_year_ago = (
            datetime.now() - timedelta(days=365)
        ).strftime("%Y-%m-%d")

        try:

            if tickers is None:
                tickers = self.get_available_tickers()[:5]

            combined_data = []

            for ticker in tickers:

                df = self.db.get_stock_data(
                    ticker, 
                    start_date = one_year_ago
                    )

                if not df.empty:

                    df_copy = df.copy()

                    df_copy["Ticker"] = ticker

                    combined_data.append(df_copy)

            if not combined_data:

                logging.warning(
                    "No data available for returns chart"
                )

                return "<p>No returns chart available.</p>"

            chart_df = pd.concat(
                combined_data,
                ignore_index=True
            )

            chart_df["Daily_Return_Pct"] = (
                chart_df["Daily_Return"] * 100
            )

            fig = px.line(
                chart_df,
                x="Date",
                y="Daily_Return_Pct",
                color="Ticker",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                title="Daily Return Comparison"
            )

            fig.update_layout(
                template="plotly_white",
                height=500,
                yaxis_title="Return (%)"
            )

            logging.info(
                "Returns chart created successfully"
            )

            return fig.to_html(
                full_html=False,
                include_plotlyjs=False
            )

        except Exception as e:

            logging.error(
                f"Returns chart creation failed: {e}"
            )

            return (
                "<p>Error generating "
                "returns chart.</p>"
            )

    def build_html_report(
        self,
        metrics,
        predictions,
        price_chart,
        volume_chart,
        returns_chart
    ):
        """
        Build professional HTML report.
        """

        logging.info(
            "Building HTML report"
        )

        prediction_rows = ""

        for pred in predictions:

            signal_color = "#ff9800"  # Default color for neutral signals

            if "STRONG BUY" in pred["signal"]:
                signal_color = "#0cd70c"

            elif "BUY" in pred["signal"]:
                signal_color = "#009900"

            elif "SELL" in pred["signal"]:
                signal_color = "#d60000"

            elif "STRONG SELL" in pred["signal"]:
                signal_color = "#ff0000"


            prediction_rows += f"""
            <tr>
                <td>{pred['ticker']}</td>
                <td>${pred['current_price']:.2f}</td>
                <td>${pred['predicted_price']:.2f}</td>
                <td>{pred['expected_return_pct']:.2f}%</td>
                <td style="color:{signal_color};
                           font-weight:bold;">
                    {pred['signal']}
                </td>
                <td>{pred['confidence']}</td>
            </tr>
            """
        average_return_color = "#27ae60"

        if metrics["average_daily_return"] < 0:
            average_return_color = "#e74c3c"

        html_content = f"""
            <!DOCTYPE html>
            <html>

            <head>

            <title>
            Financial Analytics Report
            </title>

            <style>

            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #c5d7eb;
            }}

            .header {{
                background: #4d7ba8;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}

            .header h1 {{
                font-size: 42px;
                margin-bottom: 10px;
                color: #fafafa;
            }}

            .header p {{
                font-size: 16px;
                color: #fafafa;
            }}

            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }}

            .metric-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 15px;
                margin-top: 20px;
            }}

            .metric-card {{
                background: #f4f2eb;
                padding: 15px;
                border-radius: 8px;
                min-width: 220px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;

            }}

            .section {{
                background: #f4f2eb;
                margin-top: 20px;
                padding: 20px;
                border-radius: 10px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th, td {{
                padding: 10px;
                border: 1px solid #ddd;
            }}

            th {{
                background-color: #f4f4f4;
            }}

            </style>

            </head>

            <body>

            <div class="header">

            <h1>
            📊 Financial Analytics Report
            </h1>

            <p>
            Generated:
            {metrics['report_date']}
            </p>

            </div>

            <div class="metric-container">

            <div class="metric-card">
            <h3>Total Tickers</h3>
            <small>Unique stocks analyzed</small>
            <p class="metric-value">
            {metrics['total_tickers_analyzed']}
            </p>
            </div>

            <div class="metric-card">
            <h3>Average Return</h3>
            <small>Mean daily return across all analyzed stocks</small>
            <p
                class="metric-value"
                style="color:{average_return_color};"
            >
            {metrics['average_daily_return']}%
            </p>
            </div>

            <div class="metric-card">
            <h3>Total Volume</h3>
            <small>Total volume traded across all analyzed stocks</small>
            <p class="metric-value">
            {metrics['total_volume_traded']:,}
            </p>
            </div>

            <div class="metric-card">
            <h3>Data Points</h3>
            <small>Total historical records analyzed</small>
            <p class="metric-value">
            {metrics['data_points_analyzed']}
            </p>
            </div>

            </div>

            <div class="section">

            <h2>
            🔮 Trading Signals
            </h2>

            <table>

            <tr>
            <th>Ticker</th>
            <th>Current Price</th>
            <th>Predicted Price</th>
            <th>Expected Return</th>
            <th>Signal</th>
            <th>Confidence</th>
            </tr>

            {prediction_rows}

            </table>

            </div>

            <div class="section">

            <h2>
            📈 Price Trend Analysis
            </h2>

            {price_chart}

            </div>

            <div class="section">

            <h2>
            📊 Volume Analysis
            </h2>

            {volume_chart}

            </div>

            <div class="section">

            <h2>
            📉 Returns Analysis
            </h2>

            {returns_chart}

            </div>

            <div class="section">

            <hr>

            <p>
            <em>
            This report was automatically generated by the
            Financial Analytics Reporting System.
            </em>
            </p>

            <p>
            Generated at:
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>

            </div>

            </body>
            </html>
            """

        logging.info(
            "HTML report built successfully"
        )

        return html_content

    def save_html_report(self, html_content):
        """
        Save HTML report to disk with timestamp.
        """

        filename = (
            "financial_report.html"
        )

        output_path = os.path.join(
            self.clean_dir,
            filename
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html_content)

        logging.info(
            f"Report saved: {output_path}"
        )

        return output_path

    def generate_full_report(self):
        """
        Main report generation workflow.
        """

        try:

            logging.info(
                "Starting report generation"
            )

            latest_prices = (
                self.db.get_latest_prices()
            )

            self.validate_data(
                latest_prices
            )

            metrics = (
                self.generate_metrics(
                    latest_prices
                )
            )

            predictions = (
                self.generate_predictions(
                    limit=10
                )
            )

            price_chart = (
                self.create_price_chart()
            )

            volume_chart = (
                self.create_volume_chart()
            )

            returns_chart = (
                self.create_returns_chart()
            )

            html_content = (
                self.build_html_report(
                    metrics,
                    predictions,
                    price_chart,
                    volume_chart,
                    returns_chart
                )
            )

            report_path = (
                self.save_html_report(
                    html_content
                )
            )

            logging.info(
                "Report generation completed"
            )

            return report_path

        except Exception as e:

            logging.error(
                f"Report generation failed: {e}"
            )

            raise