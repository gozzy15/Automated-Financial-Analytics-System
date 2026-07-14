import pandas as pd
import numpy as np
from utils.logger import logger

class AnalyticsService:
    """
    Handles all financial analytics and risk calculations.

    This service sits above the DatabaseHandler.
    It receives stock data (DataFrames) and computes
    portfolio statistics, risk metrics, summaries,
    recommendations, and other analytics.
    """

    def __init__(self, data_service):
        self.data_service = data_service

    def calculate_risk_statistics(
        self,
        selected_tickers,
        start_date,
        end_date
    ):
        """
        Calculate average risk statistics for the selected tickers.

        Returns
        -------
        dict | None
        """
        logger.info(
            "Calculating risk statistics for %d ticker(s).",
            len(selected_tickers)
        )

        if not selected_tickers:
            return None

        if isinstance(selected_tickers, str):
            selected_tickers = [selected_tickers]

        sharpe_list = []
        drawdown_list = []
        volatility_list = []
        var_list = []

        for ticker in selected_tickers:

            df = self.data_service.get_stock_data(
                ticker,
                start_date,
                end_date
            )

            if df.empty or len(df) < 2:
                continue

            returns = df["Daily_Return"].dropna()

            if len(returns) < 2:
                continue

            risk_free_rate = 0.02

            sharpe = (
                (returns.mean() * 252 - risk_free_rate)
                / (returns.std() * np.sqrt(252))
            )

            annual_volatility = (
                returns.std()
                * np.sqrt(252)
                * 100
            )

            cumulative = (1 + returns).cumprod()

            running_max = cumulative.cummax()

            drawdown = (
                cumulative - running_max
            ) / running_max

            max_drawdown = drawdown.min() * 100

            var95 = np.percentile(
                returns,
                5
            ) * 100

            sharpe_list.append(sharpe)
            drawdown_list.append(max_drawdown)
            volatility_list.append(annual_volatility)
            var_list.append(var95)

        if not sharpe_list:
            return None

        avg_sharpe = np.mean(sharpe_list)
        avg_drawdown = np.mean(drawdown_list)
        avg_volatility = np.mean(volatility_list)
        avg_var = np.mean(var_list)

        # Sharpe Rating
        if avg_sharpe >= 1:
            sharpe_status = "🟢 Excellent"
        elif avg_sharpe >= 0:
            sharpe_status = "🟠 Moderate"
        else:
            sharpe_status = "🔴 Poor"

        # Drawdown Rating
        if avg_drawdown > -10:
            drawdown_status = "🟢 Low Risk"
        elif avg_drawdown > -20:
            drawdown_status = "🟠 Moderate Risk"
        else:
            drawdown_status = "🔴 High Risk"

        # Volatility Rating
        if avg_volatility < 20:
            volatility_status = "🟢 Low"
        elif avg_volatility < 35:
            volatility_status = "🟠 Medium"
        else:
            volatility_status = "🔴 High"

        # VaR Rating
        if avg_var > -2:
            var_status = "🟢 Low"
        elif avg_var > -5:
            var_status = "🟠 Moderate"
        else:
            var_status = "🔴 High"

        logger.info(
            "Risk statistics calculated successfully."
        )

        return {

            "sharpe": avg_sharpe,
            "drawdown": avg_drawdown,
            "volatility": avg_volatility,
            "var": avg_var,

            "sharpe_status": sharpe_status,
            "drawdown_status": drawdown_status,
            "volatility_status": volatility_status,
            "var_status": var_status

        }
    
    def calculate_metrics(self):
        """Calculate key financial metrics"""
        logger.info(
            "Calculating dashboard metrics."
        )

        conn = self.data_service.get_connection()
        
        try:
            # Overall metrics
            overall_query = """
            SELECT 
                COUNT(DISTINCT Ticker) as Total_Tickers,
                COUNT(*) as Total_Records,
                MIN(Date) as Earliest_Date,
                MAX(Date) as Latest_Date,
                AVG(Daily_Return) * 100 as Avg_Daily_Return,
                AVG(Volume) as Avg_Volume
            FROM stock_prices
            """
            overall_df = pd.read_sql_query(overall_query, conn)
            
            # If no data, return empty
            if overall_df.empty or overall_df['Total_Records'].iloc[0] == 0:
                return pd.DataFrame({
                    'Total_Tickers': [0],
                    'Total_Records': [0],
                    'Earliest_Date': [''],
                    'Latest_Date': [''],
                    'Avg_Daily_Return': [0],
                    'Avg_Volume': [0]
                }), pd.DataFrame()
            
            # Get all data and calculate in pandas
            all_data = pd.read_sql_query("SELECT * FROM stock_prices", conn)
            
            # Calculate metrics per ticker using pandas (not SQL)
            metrics = []
            for ticker in all_data['Ticker'].unique():
                ticker_data = all_data[all_data['Ticker'] == ticker]
                
                if len(ticker_data) > 0:
                    metrics.append({
                        'Ticker': ticker,
                        'Records': len(ticker_data),
                        'Avg_Return': round(
                            ticker_data['Daily_Return'].mean() * 100,
                            2
                        ) if len(ticker_data) > 0 else 0.00,
                        'Volatility': round(
                            ticker_data['Daily_Return'].std() * 100,
                            2
                        ) if len(ticker_data) > 1 else 0.00,
                        'Period_High': round(
                            ticker_data['High'].max(),
                            4
                        ),
                        'Period_Low': round(
                            ticker_data['Low'].min(),
                            4
                        ),
                        'Avg_Volume': round(
                            ticker_data['Volume'].mean(),
                            0
                        )
                    })
            
            ticker_df = pd.DataFrame(metrics)
            ticker_df = ticker_df.sort_values('Avg_Return', ascending=False)
            
            logger.info(
                "Dashboard metrics calculated successfully."
            )

            return overall_df, ticker_df
            
        except Exception:
            logger.exception("Failed to calculate dashboard metrics.")

            # Return empty dataframes on error
            return pd.DataFrame({
                'Total_Tickers': [0],
                'Total_Records': [0],
                'Earliest_Date': [''],
                'Latest_Date': [''],
                'Avg_Daily_Return': [0],
                'Avg_Volume': [0]
            }), pd.DataFrame()
        finally:
            conn.close()

    def generate_executive_summary(
        self,
        selected_tickers,
        start_date,
        end_date
    ):
        """
        Generate executive summary statistics.

        Returns
        -------
        dict
        """
        logger.info(
            "Generating executive summary."
        )

        metrics = []
        stock_data = {}

        if not selected_tickers:
            return pd.DataFrame(), {}

        for ticker in selected_tickers:

            df = self.data_service.get_stock_data(
                ticker,
                start_date,
                end_date
            )

            if df.empty:
                logger.warning(
                    "No stock data available for %s.",
                    ticker
                )
                continue
            

            stock_data[ticker] = df

            metrics.append({

                "Ticker": ticker,

                "Avg_Return": df["Daily_Return"].mean() * 100,

                "Volatility": df["Daily_Return"].std() * 100,

                "Avg_Volume": df["Volume"].mean()

            })

        metrics = pd.DataFrame(metrics)

        logger.info(
            "Executive summary generated successfully."
        )

        return metrics, stock_data