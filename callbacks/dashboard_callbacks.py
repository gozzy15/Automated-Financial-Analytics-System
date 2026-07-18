import pandas as pd
from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from zoneinfo import ZoneInfo
from system_config import TIMEZONE
import plotly.graph_objects as go
from financial_scraper import FinancialScraper

from visualization.charts import (
    create_main_chart,
    create_secondary_chart,
    create_correlation_heatmap,
    create_scatter_matrix
)

def register_dashboard_callbacks(
    app,
    data_service,
    analytics_service
):

    # Callbacks for interactivity
    @app.callback(
        [
            Output("main-chart", "figure"),
            Output("secondary-chart", "figure"),
            Output("data-table", "columns"),
            Output("data-table", "data"),
            Output("data-store", "data"),
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
            Input("analysis-type", "value"),
        ]
    )

    def update_dashboard(selected_tickers, start_date, end_date, analysis_type):
        """Update dashboard based on user inputs"""
        
        if not selected_tickers:

            available_tickers = data_service.get_all_tickers()

            selected_tickers = (
                available_tickers[:1]
                if available_tickers
                else []
            )
        
        # Get data for selected tickers
        all_data, combined_df = data_service.load_data(
            selected_tickers,
            start_date,
            end_date
        )
        
        if not all_data:
            # Return empty figures if no data
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for selected criteria",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            
            return empty_fig, empty_fig, [], [], {}
        
        # Create main chart based on analysis type
        latest_prices = data_service.get_latest_data()

        main_fig = create_main_chart(
            all_data,
            analysis_type,
            latest_prices
        )
        
        # Create secondary chart
        secondary_fig = create_secondary_chart(all_data, analysis_type)
        
        # -----------------------------------
        # Format numeric columns for display
        # -----------------------------------

        display_df = combined_df.copy()

        # Columns that should display 2 decimal places
        price_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Daily_Return",
            "Cumulative_Return",
            "SMA_20",
            "SMA_50",
            "RSI"
        ]

        for column in price_columns:

            if column in display_df.columns:

                display_df[column] = (
                    display_df[column]
                    .round(2)
                )

        # Prepare table
        table_columns = [
            {
                "name": col.replace("_", " "),
                "id": col
            }
            for col in display_df.columns
        ]

        table_data = display_df.to_dict("records")

        # Keep original precision for downloads
        store_data = (
            combined_df.to_dict("records")
            if not combined_df.empty
            else {}
        )
        
        return main_fig, secondary_fig, table_columns, table_data, store_data
    

    @app.callback(
        [
            Output("label-1", "children"),
            Output("best-performer", "children"),

            Output("label-2", "children"),
            Output("worst-performer", "children"),

            Output("label-3", "children"),
            Output("most-volatile", "children"),

            Output("label-4", "children"),
            Output("highest-volume", "children"),

            Output("label-5", "children"),
            Output("average-return", "children"),

            Output("market-insights", "children")
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
        ]
    )

    def update_executive_summary(selected_tickers, start_date, end_date):

        if not selected_tickers:

            return (

                "🏆 Best Performer",
                "N/A",

                "📉 Worst Performer",
                "N/A",

                "⚡ Most Volatile",
                "N/A",

                "💹 Highest Volume",
                "N/A",

                "📊 Average Return",
                "N/A",

                []

            )

        metrics, stock_data = analytics_service.generate_executive_summary(
            selected_tickers,
            start_date,
            end_date
        )

        if metrics.empty:

            return (

                "🏆 Best Performer",
                "N/A",

                "📉 Worst Performer",
                "N/A",

                "⚡ Most Volatile",
                "N/A",

                "💹 Highest Volume",
                "N/A",

                "📊 Average Return",
                "N/A",

                []

            )

        # ======================================================
        # SINGLE STOCK
        # ======================================================

        if len(metrics) == 1:

            stock = metrics.iloc[0]
            df = stock_data[stock["Ticker"]]

            insights = [

                html.Li(
                    f"{stock['Ticker']} generated an average daily return of {stock['Avg_Return']:.2f}%."
                ),

                html.Li(
                    f"Average daily volatility was {stock['Volatility']:.2f}%."
                ),

                html.Li(
                    f"Average trading volume was {stock['Avg_Volume']:,.0f} shares."
                ),

                html.Li(
                    f"The stock traded between ${df['Low'].min():.2f} and ${df['High'].max():.2f} during the selected period."
                )

            ]

            return (

                "📌 Selected Stock",
                stock["Ticker"],

                "📈 Average Return",
                f"{stock['Avg_Return']:.2f}%",

                "📊 Volatility",
                f"{stock['Volatility']:.2f}%",

                "💹 Average Volume",
                f"{stock['Avg_Volume']:,.0f}",

                "📏 Price Range",
                f"${df['Low'].min():.2f} → ${df['High'].max():.2f}",

                insights

            )

        # ======================================================
        # MULTIPLE STOCKS
        # ======================================================

        best = metrics.loc[metrics["Avg_Return"].idxmax()]
        worst = metrics.loc[metrics["Avg_Return"].idxmin()]
        volatile = metrics.loc[metrics["Volatility"].idxmax()]
        volume = metrics.loc[metrics["Avg_Volume"].idxmax()]

        average = metrics["Avg_Return"].mean()

        insights = [

            html.Li(
                f"{best['Ticker']} delivered the strongest average return ({best['Avg_Return']:.2f}%)."
            ),

            html.Li(
                f"{worst['Ticker']} produced the weakest average return ({worst['Avg_Return']:.2f}%)."
            ),

            html.Li(
                f"{volatile['Ticker']} exhibited the highest volatility ({volatile['Volatility']:.2f}%)."
            ),

            html.Li(
                f"{volume['Ticker']} recorded the highest average trading volume ({volume['Avg_Volume']:,.0f})."
            ),

            html.Li(
                f"The selected portfolio achieved an average daily return of {average:.2f}%."
            )

        ]

        return (

            "🏆 Best Performer",
            f"{best['Ticker']} ({best['Avg_Return']:.2f}%)",

            "📉 Worst Performer",
            f"{worst['Ticker']} ({worst['Avg_Return']:.2f}%)",

            "⚡ Most Volatile",
            f"{volatile['Ticker']} ({volatile['Volatility']:.2f}%)",

            "💹 Highest Volume",
            f"{volume['Ticker']} ({volume['Avg_Volume']:,.0f})",

            "📊 Average Return",
            f"{average:.2f}%",

            insights

        )
    

    @app.callback(
        [
            Output("kpi-total-tickers", "children"),
            Output("kpi-total-records", "children"),
            Output("kpi-start-date", "children"),
            Output("kpi-end-date", "children"),
            Output("kpi-average-return", "children"),
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date"),
        ]
    )

    def update_kpi_cards(selected_tickers, start_date, end_date):

        if not selected_tickers:
            return "0", "0", "-", "-", "0.00%"

        if isinstance(selected_tickers, str):
            selected_tickers = [selected_tickers]

        combined = []

        for ticker in selected_tickers:

            df = data_service.get_stock_data(
                ticker,
                start_date,
                end_date
            )

            if not df.empty:
                combined.append(df)

        if not combined:
            return (
                "0",
                "0",
                "-",
                "-",
                "0.00%"
            )

        df = pd.concat(
            combined,
            ignore_index=True
        )

        print("=" * 60)
        print(df[["Ticker", "Date"]])
        print(f"Rows: {len(df)}")
        print("=" * 60)

        total_tickers = len(selected_tickers)

        total_records = len(df)

        start = df["Date"].min()[:10]

        end = df["Date"].max()[:10]

        avg_return = df["Daily_Return"].mean() * 100

        return (

            f"{total_tickers}",

            f"{total_records:,}",

            start,

            end,

            f"{avg_return:.2f}%"

        )
    
    
    @app.callback(
        [
            Output("sharpe-ratio", "children"),
            Output("max-drawdown", "children"),
            Output("annual-volatility", "children"),
            Output("value-at-risk", "children")
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
        ]
    )
    
    def update_risk_metrics(selected_tickers, start_date, end_date):

        metrics = analytics_service.calculate_risk_statistics(
            selected_tickers,
            start_date,
            end_date
        )

        if metrics is None:
            return "N/A", "N/A", "N/A", "N/A"

        avg_sharpe = metrics["sharpe"]
        avg_drawdown = metrics["drawdown"]
        avg_volatility = metrics["volatility"]
        avg_var = metrics["var"]

        sharpe_status = metrics["sharpe_status"]
        drawdown_status = metrics["drawdown_status"]
        volatility_status = metrics["volatility_status"]
        var_status = metrics["var_status"]

        return (

            html.Div([
                html.H4(f"{avg_sharpe:.2f}"),
                html.Small(sharpe_status)
            ]),

            html.Div([
                html.H4(f"{avg_drawdown:.2f}%"),
                html.Small(drawdown_status)
            ]),

            html.Div([
                html.H4(f"{avg_volatility:.2f}%"),
                html.Small(volatility_status)
            ]),

            html.Div([
                html.H4(f"{avg_var:.2f}%"),
                html.Small(var_status)
            ])

        )
    

    @app.callback(
        [
            Output("portfolio-score", "children"),
            Output("portfolio-rating", "children"),
            Output("portfolio-comment", "children")
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
        ]
    )

    def update_portfolio_score(selected_tickers, start_date, end_date):

        if not selected_tickers:
            return "--", "", ""

        metrics = analytics_service.calculate_risk_statistics(
            selected_tickers,
            start_date,
            end_date
        )

        if metrics is None:
            return "--", "", ""

        avg_sharpe = metrics["sharpe"]
        avg_drawdown = metrics["drawdown"]
        avg_volatility = metrics["volatility"]
        avg_var = metrics["var"]

        score = 100

        # Sharpe contribution
        if avg_sharpe < 0:
            score -= 30
        elif avg_sharpe < 1:
            score -= 15

        # Drawdown contribution
        if avg_drawdown < -30:
            score -= 25
        elif avg_drawdown < -15:
            score -= 10

        # Volatility contribution
        if avg_volatility > 40:
            score -= 20
        elif avg_volatility > 25:
            score -= 10

        # VaR contribution
        if avg_var < -5:
            score -= 15
        elif avg_var < -2:
            score -= 8

        score = max(0, min(100, round(score)))

        if score >= 90:
            rating = "★★★★★ Excellent"
            comment = (
                "The portfolio demonstrates excellent risk-adjusted performance with "
                "healthy volatility and controlled downside risk."
            )

        elif score >= 75:
            rating = "★★★★☆ Very Good"
            comment = (
                "Overall portfolio quality is strong, with acceptable risk levels "
                "and solid return characteristics."
            )

        elif score >= 60:
            rating = "★★★☆☆ Good"
            comment = (
                "The portfolio is reasonably balanced but has room for improvement "
                "in risk management or returns."
            )

        elif score >= 40:
            rating = "★★☆☆☆ Fair"
            comment = (
                "The portfolio carries noticeable risk. Consider reviewing "
                "asset selection and diversification."
            )

        else:
            rating = "★☆☆☆☆ Poor"
            comment = (
                "The portfolio exhibits weak risk-adjusted performance and "
                "high downside risk."
            )

        return (
            f"{score}/100",
            rating,
            comment
        )
    

    @app.callback(
        [
            Output("portfolio-action", "children"),
            Output("portfolio-reason", "children")
        ],
        [
            Input("ticker-dropdown", "value"),
            Input("date-picker", "start_date"),
            Input("date-picker", "end_date")
        ]
    )
   
    def update_recommendation(selected_tickers, start_date, end_date):

        if not selected_tickers:
            return "No Recommendation", "Please select at least one ticker."

        metrics = analytics_service.calculate_risk_statistics(
            selected_tickers,
            start_date,
            end_date
        )

        if metrics is None:
            return "No Recommendation", "Insufficient data."

        avg_sharpe = metrics["sharpe"]
        avg_drawdown = metrics["drawdown"]
        avg_volatility = metrics["volatility"]
        avg_var = metrics["var"]

        score = 100

        if avg_sharpe < 0:
            score -= 30
        elif avg_sharpe < 1:
            score -= 15

        if avg_drawdown < -30:
            score -= 25
        elif avg_drawdown < -15:
            score -= 10

        if avg_volatility > 40:
            score -= 20
        elif avg_volatility > 25:
            score -= 10

        if avg_var < -5:
            score -= 15
        elif avg_var < -2:
            score -= 8

        score = max(0, min(100, round(score)))

        if score >= 90:
            action = "🟢 STRONG BUY"
            reason = (
                "Excellent risk-adjusted returns, low downside risk, "
                "and healthy volatility indicate a high-quality portfolio."
            )

        elif score >= 75:
            action = "🟢 BUY"
            reason = (
                "The portfolio shows solid performance with acceptable risk. "
                "Current indicators remain favorable."
            )

        elif score >= 60:
            action = "🟡 HOLD"
            reason = (
                "Performance is stable. Maintaining the current allocation "
                "while monitoring market conditions is reasonable."
            )

        elif score >= 40:
            action = "🟠 REDUCE EXPOSURE"
            reason = (
                "Portfolio risk is increasing. Consider reducing positions "
                "or improving diversification."
            )

        else:
            action = "🔴 HIGH RISK"
            reason = (
                "Risk metrics indicate elevated downside risk and weak "
                "risk-adjusted performance."
            )

        return action, reason
    
    @app.callback(
        Output("current-time", "children"),
        Input("clock-interval", "n_intervals")
    )
    def update_clock(n):

        nigeria_time = datetime.now(
            ZoneInfo(TIMEZONE)
        )

        return nigeria_time.strftime(
            "%A, %d %B %Y  |  %I:%M:%S %p"
        )
    
    @app.callback(

        Output("main-chart-title", "children"),
        Output("main-chart-description", "children"),
        Output("secondary-chart-title", "children"),
        Output("secondary-chart-description", "children"),

        Input("analysis-type", "value"),
        Input("ticker-dropdown", "value")

    )

    def update_chart_headers(analysis_type, selected_tickers):

        ticker_count = len(selected_tickers) if selected_tickers else 0

        # ------------------------
        # Main Chart
        # ------------------------

        if analysis_type == "price":

            main_title = "📈 Price & Volume Analysis"

            main_desc = (
                "Interactive candlestick chart showing historical price movements "
                "and trading volume."
            )

        elif analysis_type == "technical":

            main_title = "📊 Technical Indicators"

            main_desc = (
                "Analyze moving averages, RSI and daily returns to identify "
                "market trends."
            )

        elif analysis_type == "returns":

            main_title = "📉 Cumulative Returns"

            main_desc = (
                "Track cumulative investment performance throughout the selected period."
            )

        elif analysis_type == "portfolio":

            main_title = "💼 Portfolio Analysis"

            main_desc = (
                "Review portfolio allocation and compare individual stock performance."
            )

        else:

            main_title = "📦 Trading Volume Analysis"

            main_desc = (
                "Visualize trading activity and identify changes in market participation."
            )

        # ------------------------
        # Secondary Chart
        # ------------------------

        if ticker_count <= 1:

            secondary_title = "📊 Return Distribution"

            secondary_desc = (
                "Histogram showing how daily returns are distributed for the selected stock."
            )

        else:

            secondary_title = "📈 Comparative Performance"

            secondary_desc = (
                "Normalized price comparison across all selected stocks."
            )

        return (

            main_title,
            main_desc,
            secondary_title,
            secondary_desc

        )
    
    @app.callback(
        Output("download-data", "data"),
        Input("download-button", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )

    def download_data(n_clicks, stored_data):
        """Download data as CSV"""
        if stored_data:
            df = pd.DataFrame(stored_data)
            return dcc.send_data_frame(df.to_csv, "financial_data.csv")
        return None
    
    @app.callback(
        Output('live-quotes', 'children'),
        [Input('interval-component', 'n_intervals'),
        Input('ticker-dropdown', 'value')]
    )
    def update_live_quotes(n_intervals, selected_tickers):
        """Update live quotes"""
        if not selected_tickers:
            return "Select ticker(s) to see live data"
        
        try:
            # Ensure selected_tickers is a list
            if isinstance(selected_tickers, str):
                tickers_list = [selected_tickers]
            else:
                tickers_list = selected_tickers
            
            # Limit to 3 tickers for performance
            display_tickers = tickers_list[:3]
            
            scraper = FinancialScraper()
            realtime_data = scraper.get_realtime_tickers_data(display_tickers)
            
            quotes = []
            for ticker in display_tickers:
                if ticker in realtime_data and 'error' not in realtime_data[ticker]:
                    data = realtime_data[ticker]
                    
                    # Calculate color based on change
                    change_color = 'green' if data.get('close', 0) >= data.get('open', 0) else 'red'
                    
                    quotes.append(
                        dbc.Row([
                            dbc.Col(html.Strong(ticker), width=2),
                            dbc.Col(html.Span(f"${data.get('close', 0):.2f}", 
                                    style={'color': change_color, 'fontWeight': 'bold'}), width=3),
                            dbc.Col(html.Small(f"Vol: {data.get('volume', 0):,}"), width=4),
                            dbc.Col(html.Small(data.get('last_updated', '')[:16]), width=3)
                        ], className="mb-2")
                    )
            
            return quotes if quotes else "No live data available"
            
        except Exception as e:
            return f"Error loading live data: {str(e)[:50]}"

    @app.callback(
        [Output('correlation-heatmap', 'figure'),
        Output('scatter-matrix', 'figure')],
        [Input('ticker-dropdown', 'value'),
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date')]
    )

    def update_correlation_analysis(selected_tickers, start_date, end_date):
        """Update correlation analysis"""
        
        if not selected_tickers or len(selected_tickers) < 2:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Select at least 2 tickers for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig
        
        # Get data and create correlation matrix
        price_data = {}
        
        for ticker in selected_tickers:
            df = data_service.get_stock_data(ticker, start_date, end_date)
            if not df.empty:
                price_data[ticker] = df.set_index('Date')['Close']
        
        if len(price_data) < 2:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Insufficient data for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return empty_fig, empty_fig
        
        # Create DataFrame
        combined = pd.DataFrame(price_data)
        
        # Calculate returns
        returns = combined.pct_change().dropna()
        
        heatmap_fig = create_correlation_heatmap(returns)
        
        scatter_fig = create_scatter_matrix(returns)
        
        return heatmap_fig, scatter_fig