import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from datetime import datetime, timedelta
from database_manager import DatabaseHandler
import os
from utils.logger import logger
from system_config import MODELS_PATH

class FinancialPredictor:
    def __init__(self):
        self.db_handler = DatabaseHandler()
        # Cache trained models in memory
        self.models = {}
        
        os.makedirs(MODELS_PATH, exist_ok=True)
        
    def prepare_features(self, df: pd.DataFrame, forecast_days: int = 7) -> tuple:
        """Prepare features for machine learning"""
        # Create lag features
        for lag in [1, 3, 5, 7]:
            # sift  get past values by moving data down
            df[f'Close_lag_{lag}'] = df['Close'].shift(lag)
            df[f'Volume_lag_{lag}'] = df['Volume'].shift(lag)
        
        # Rolling statistics 
        # rolling(window=7) = look at last 7 values and calculate mean and std
        df['Close_rolling_mean_7'] = df['Close'].rolling(window=7).mean()
        df['Close_rolling_std_7'] = df['Close'].rolling(window=7).std()
        df['Volume_rolling_mean_7'] = df['Volume'].rolling(window=7).mean()
        
        # Technical indicators (if not already present)
        if 'RSI' not in df.columns:
            # Difference between today’s price and yesterday’s price
            delta = df['Close'].diff()
            # Calculate average gain and loss over the past 14 days
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            # Calculate Relative Strength (RS) and Relative Strength Index (RSI)
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        # Target variable: Future close price
        df['Target'] = df['Close'].shift(-forecast_days)
        
        # Drop NaN
        df = df.dropna()

        excluded_columns = {
            "Date",
            "Target",
            "Ticker",
            "Processing_Date"
        }
        
        # Feature columns
        feature_cols = [
            column
            for column in df.columns
            if column not in excluded_columns
        ]
        
        return df[feature_cols], df['Target'], df['Date']
    
    def train_model(self, ticker: str):
        """Train prediction model for specific ticker"""
        # Get data from database
        # Fetch stock data for the given ticker from the database
        df = self.db_handler.get_stock_data(ticker)
        # Sort into chronological order for feature engineering
        df = df.sort_values("Date").reset_index(drop=True)
        try:
            if len(df) < 50:
                logger.warning(
                    "Not enough historical data to train model for %s",
                    ticker
                )
                return None
            
            # Prepare features
            X, y, dates = self.prepare_features(df)
            
            if len(X) < 30:
                logger.warning(
                    "Not enough training samples for %s",
                    ticker
                )
                return None
            
            # Split data
            X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
                X, y, dates, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            logger.info(
                "Model trained for %s | MAE=%.2f | RMSE=%.2f",
                ticker,
                mae,
                rmse
            )
            
            # Save model and scaler
            self.models[ticker] = {
                'model': model,
                'scaler': scaler,
                'feature_names': X.columns.tolist(),
                'metrics': {'MAE': mae, 'RMSE': rmse}
            }

            # Ensure models directory exists
            os.makedirs(MODELS_PATH, exist_ok=True)
            
            # Save to file
            # Save trained model and scaler to disk for later use (no need to retrain)
            joblib.dump(model, f'{MODELS_PATH}/{ticker}_model.pkl')
            joblib.dump(scaler, f'{MODELS_PATH}/{ticker}_scaler.pkl')
            
            return self.models[ticker]
        
        except Exception:

            logger.exception(
                "Failed to train model for %s",
                ticker
            )

            return None
    
    
    def predict_future(self, ticker: str, days_ahead: int = 7):
        """Predict future prices"""
        try:
            if ticker not in self.models:
                logger.info(
                    "Training model for %s",
                    ticker
                )
                self.train_model(ticker)
            
            # Get latest data
            df = self.db_handler.get_stock_data(ticker)
            # Sort into chronological order for feature engineering
            df = df.sort_values("Date").reset_index(drop=True)
            last_trading_date = pd.to_datetime(df['Date'].iloc[-1])
            prediction_date = last_trading_date + pd.offsets.BusinessDay(days_ahead)
            
            if len(df) < 50:
                logger.warning(
                    "Prediction skipped for %s because fewer than 50 records were found.",
                    ticker
                )

                return None
                
            
            # Prepare features for prediction
            X, y, _ = self.prepare_features(
                df,
                forecast_days=days_ahead
            )
            
            if len(X) == 0:
                return None
            
            # Use the latest data point for prediction
            latest_features = X.iloc[[-1]]
            
            # Scale features
            scaler = self.models[ticker]['scaler']
            latest_features_scaled = scaler.transform(latest_features)
            
            # Make prediction
            model = self.models[ticker]['model']
            prediction = model.predict(latest_features_scaled)[0]
            
            # Get feature importance
            feature_importance = pd.DataFrame({
                'feature': self.models[ticker]['feature_names'],
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Calculate confidence interval (simplified)
            y_pred_all = model.predict(scaler.transform(X))
            residuals = y.values - y_pred_all
            std_residuals = np.std(residuals)
            
            ci_lower = prediction - 1.96 * std_residuals
            ci_upper = prediction + 1.96 * std_residuals
            
            current_price = float(df['Close'].iloc[-1])
            # Prediction payload returned to dashboard
            result = {
                'ticker': ticker,
                'prediction_date': prediction_date.strftime('%Y-%m-%d'),
                'predicted_close': float(prediction),
                'ci_lower': float(ci_lower),
                'ci_upper': float(ci_upper),
                'current_price': current_price,
                'expected_return': float(
                                        (prediction - current_price)
                                        / current_price * 100
                                    ),
                'feature_importance': feature_importance.head(10).to_dict('records'),
                'model_metrics': self.models[ticker]['metrics']
            }
            
            # Save prediction to database
            self.db_handler.save_prediction(result)
            
            return result
        
        except Exception:
            logger.exception(
                "Failed to predict future prices for %s",
                ticker
            )
            return None
    
    def generate_trading_signals(self, ticker: str):
        """Generate trading signals based on predictions"""
        prediction = self.predict_future(ticker)
        
        try:
            if not prediction:
                return None
            
            current_price = prediction['current_price']
            predicted_price = prediction['predicted_close']
            
            # Simple signal logic
            price_change_pct = prediction['expected_return']
            
            if price_change_pct > 5:
                signal = "STRONG BUY"
                confidence = "HIGH"
            elif price_change_pct > 2:
                signal = "BUY"
                confidence = "MEDIUM"
            elif price_change_pct < -5:
                signal = "STRONG SELL"
                confidence = "HIGH"
            elif price_change_pct < -2:
                signal = "SELL"
                confidence = "MEDIUM"
            else:
                signal = "HOLD"
                confidence = "LOW"
            
            return {
                'ticker': ticker,
                'signal': signal,
                'confidence': confidence,
                'current_price': current_price,
                'predicted_price': predicted_price,
                'expected_return_pct': price_change_pct,
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            logger.exception(
                "Failed to generate trading signal for %s",
                ticker
            )
            return None