import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import MetaTrader5 as MT5


class GoldPricePredictorM5:
    def __init__(self, pair, days: int = 7, test_size: float = 0.2, random_state: int = 42): #: str = 'XAUUSDb'
        self.Pair = pair
        """Initialize the Gold Price Predicctor for 5-minute intervals"""
        self.days = days  # Maximum 7 days for 5-minute data
        self.test_size = test_size
        self.random_state = random_state
        self.model = None
        self.latest_data = None
        self.current_price = None
        self.current_time = None
        self.predicted_time = None
        self.data_start = None
        self.data_end = None
        self.df = None
        self.metrics = {}
        self.confidence_metrics = {}
        self.scaler = StandardScaler()

    def get_gold_data(self) -> Optional[pd.DataFrame]:
        """Get gold price data from MetaTrader 5 (5-minute timeframe)"""
        try:
            if not MT5.initialize():
                raise RuntimeError("MT5 initialization failed")

            #print(f"Fetching 5-minute data for: {self.Pair}")
            RatesM5 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 2500)
            if RatesM5 is None:
                raise ValueError("Failed to fetch data from MT5")

            FrameRatesM5 = pd.DataFrame(RatesM5)
            if FrameRatesM5.empty:
                raise ValueError("DataFrame is empty")

        # پردازش داده‌ها
            FrameRatesM5['datetime'] = pd.to_datetime(FrameRatesM5['time'], unit='s')
            FrameRatesM5.set_index(pd.DatetimeIndex(FrameRatesM5['datetime']), inplace=True, drop=True)
            FrameRatesM5.drop(columns=['time'], inplace=True)

        # تغییر نام ستون‌ها برای تطبیق با کد اصلی
            FrameRatesM5.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'  # اگر tick_volume استفاده شده باشه
            }, inplace=True)

        # به‌روزرسانی ویژگی‌های کلاس
            self.df = FrameRatesM5
            self.data_start = FrameRatesM5.index[0].strftime('%Y-%m-%d %H:%M:%S')
            self.data_end = FrameRatesM5.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            self.current_price = FrameRatesM5['Close'].iloc[-1]

            # print(f"Successfully fetched {len(FrameRatesM5)} rows from MT5.")
            # print(f"Latest gold price (from MT5): ${self.current_price:.2f}")
            return FrameRatesM5

        except Exception as e:
            print(f"Error in get_gold_data: {e}")
            return None


    def prepare_data(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[pd.DataFrame]]:
        """Prepare data for training with 5-minute intervals"""
        try:
            # Create time-based features
            df['Hour'] = df.index.hour
            df['Minute'] = df.index.minute
            df['DayOfWeek'] = df.index.dayofweek
            df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
            
            # Create price features
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = df['Close'].pct_change()
            df['Volume_Change'] = df['Volume'].diff()
            df['High_Low_Diff'] = df['High'] - df['Low']
            
            # Create multiple moving averages
            df['MA_5'] = df['Close'].rolling(window=5).mean()  # 25-minute MA
            df['MA_12'] = df['Close'].rolling(window=12).mean()  # 1-hour MA
            df['MA_30'] = df['Close'].rolling(window=30).mean()  # 2.5-hour MA
            df['MA_72'] = df['Close'].rolling(window=72).mean()  # 6-hour MA
            
            # Create price momentum indicators
            df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
            df['Momentum_12'] = df['Close'] - df['Close'].shift(12)
            
            # Create volatility indicators
            df['Volatility_5'] = df['Close'].rolling(window=5).std()
            df['Volatility_12'] = df['Close'].rolling(window=12).std()
            
            # Create target (price after 30 minutes = 6 intervals of 5 minutes)
            df['Target'] = df['Close'].shift(-6)
            
            # Remove NaN values
            df = df.dropna()
            
            # Features for prediction
            features = [
                'Open', 'High', 'Low', 'Close', 'Volume',
                'Hour', 'Minute', 'DayOfWeek', 'IsWeekend',
                'Price_Change', 'Price_Change_Pct', 'Volume_Change',
                'High_Low_Diff', 'MA_5', 'MA_12', 'MA_30', 'MA_72',
                'Momentum_5', 'Momentum_12',
                'Volatility_5', 'Volatility_12'
            ]
            
            X = df[features]
            y = df['Target']
            
            return X, y, df
        except Exception as e:
            print(f"Error preparing data: {str(e)}")
            return None, None, None

    def calculate_confidence_metrics(self, y_test: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate additional confidence metrics with improved thresholds"""
        try:
            # Calculate prediction errors
            errors = np.abs(y_test - y_pred)
            
            # Calculate percentage errors
            percentage_errors = (errors / y_test) * 100
            
            # Calculate success rate with multiple thresholds
            thresholds = [0.05, 0.1, 0.2]  # 0.05%, 0.1%, 0.2%
            success_rates = {}
            for threshold in thresholds:
                successful_predictions = np.sum(percentage_errors <= threshold)
                success_rates[f'success_rate_{threshold}'] = (successful_predictions / len(y_test)) * 100
            
            # Calculate confidence intervals
            std_error = np.std(errors)
            confidence_95 = 1.96 * std_error
            confidence_99 = 2.58 * std_error
            
            # Calculate directional accuracy
            if len(y_test) > 1 and len(y_pred) > 1:
                actual_changes = np.diff(y_test)
                predicted_changes = np.diff(y_pred)
                directional_accuracy = np.mean(np.sign(actual_changes) == np.sign(predicted_changes)) * 100
            else:
                directional_accuracy = 0.0
            
            # Calculate trend accuracy
            trend_accuracy = np.mean(np.sign(y_test - y_test[0]) == np.sign(y_pred - y_pred[0])) * 100
            
            return {
                'success_rate_0.05': success_rates['success_rate_0.05'],
                'success_rate_0.1': success_rates['success_rate_0.1'],
                'success_rate_0.2': success_rates['success_rate_0.2'],
                'avg_percentage_error': np.mean(percentage_errors),
                'confidence_95': confidence_95,
                'confidence_99': confidence_99,
                'directional_accuracy': directional_accuracy,
                'trend_accuracy': trend_accuracy,
                'max_error': np.max(errors),
                'min_error': np.min(errors)
            }
        except Exception as e:
            print(f"Error calculating confidence metrics: {str(e)}")
            return {
                'success_rate_0.05': 0.0,
                'success_rate_0.1': 0.0,
                'success_rate_0.2': 0.0,
                'avg_percentage_error': 0.0,
                'confidence_95': 0.0,
                'confidence_99': 0.0,
                'directional_accuracy': 0.0,
                'trend_accuracy': 0.0,
                'max_error': 0.0,
                'min_error': 0.0
            }

    def train_model(self, X: pd.DataFrame, y: pd.Series) -> Tuple[Optional[RandomForestRegressor], Optional[pd.DataFrame], Optional[np.ndarray], Optional[np.ndarray], Optional[float], Optional[float]]:
        """Train the model with improved parameters and cross-validation"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=self.random_state)
            
            # Create pipeline with scaling and model
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('model', RandomForestRegressor(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=self.random_state
                ))
            ])
            
            # Train model
            pipeline.fit(X_train, y_train)
            self.model = pipeline
            
            # Make predictions
            y_pred = pipeline.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # Store metrics
            self.metrics = {
                'mse': mse,
                'r2': r2,
                'rmse': rmse
            }
            
            # Calculate confidence metrics
            self.confidence_metrics = self.calculate_confidence_metrics(y_test, y_pred)
            
            # Print feature importance
            #print("\nFeature Importance:")
            feature_importance = pd.DataFrame({
                'Feature': X.columns,
                'Importance': pipeline.named_steps['model'].feature_importances_
            }).sort_values('Importance', ascending=False)
            #print(feature_importance.head(10))
            
            return pipeline, X_test, y_test, y_pred, mse, r2
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None, None, None, None, None, None

    def predict_next_hour(self, latest_data: np.ndarray) -> Optional[float]:
        """Predict the next hour's gold price"""
        try:
            if self.model is None:
                raise ValueError("Model has not been trained yet")
            prediction = self.model.predict(latest_data.reshape(1, -1))
            return prediction[0]
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return None

    def plot_predictions(self, y_test: np.ndarray, y_pred: np.ndarray, show_plot: bool = True) -> None:
        """Plot actual vs predicted prices with confidence intervals"""
        try:
            plt.figure(figsize=(12, 6))
            sns.set_style('whitegrid')
            
            x_axis = range(len(y_test))
            plt.plot(x_axis, y_test, color='gold', label='Actual Gold Price', linewidth=2)
            plt.plot(x_axis, y_pred, '--', color='blue', label='Predicted Gold Price', linewidth=1.5)
            
            # Add confidence intervals
            confidence = self.confidence_metrics['confidence_95']
            plt.fill_between(x_axis, 
                           y_pred - confidence, 
                           y_pred + confidence, 
                           color='blue', 
                           alpha=0.2,
                           label='95% Confidence Interval')
            
            plt.title('Gold Price Prediction (30-Minute Forecast)')
            plt.xlabel('Time (5-minute intervals)')
            plt.ylabel('Price (USD/oz)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            if show_plot:
                plt.show(block=True)
        except Exception as e:
            print(f"Error plotting results: {str(e)}")

    def predict(self, show_plot: bool = True) -> Tuple[Dict[str, Any], Optional[float], Optional[float], Optional[float], Optional[str], Optional[str]]:
        """Run the complete prediction process for 30-minute forecast"""
        try:
            # Get and validate data
            df = self.get_gold_data()
            if df is None:
                print("Error: Could not get gold data")
                return {}, None, None, None, None, None
            
            # Prepare and validate data
            X, y, df_prepared = self.prepare_data(df)
            if X is None or y is None:
                print("Error: Could not prepare data")
                return {}, None, None, None, None, None
            
            print("\nTraining model...")
            # Train model and validate
            self.model, X_test, y_test, y_pred, mse, r2 = self.train_model(X, y)
            if self.model is None:
                print("Error: Could not train model")
                return {}, None, None, None, None, None
            
            # Get prediction components
            latest_data = X.iloc[-1:].values  # Get the last row as a 2D array
            next_price = float(self.model.predict(latest_data)[0])  # Predict and get the scalar value
            current_price = df['Close'].iloc[-1]
            
            # Get timestamps
            current_time = df.index[-1]
            predicted_time = current_time + timedelta(minutes=30)
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            predicted_time_str = predicted_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Store values
            self.current_price = current_price
            self.current_time = current_time_str
            self.predicted_time = predicted_time_str
            self.latest_data = latest_data
            
            # Calculate change
            predicted_change = next_price - current_price
            
            # Calculate confidence metrics
            self.confidence_metrics = self.calculate_confidence_metrics(y_test, y_pred)
            
            # Print detailed results
            # print("\nTime Information:")
            # print(f"Data Start: {self.data_start}")
            # print(f"Data End: {self.data_end}")
            # print(f"Current Time: {current_time_str}")
            # print(f"Prediction Time (30 min ahead): {predicted_time_str}")
            
            # print("\nGold Price Prediction Results:")
            # print(f"Model Accuracy (R2): {self.metrics['r2']:.4f}")
            # print(f"Mean Squared Error: {self.metrics['mse']:.4f}")
            # print(f"Root Mean Squared Error: {self.metrics['rmse']:.4f}")
            # print(f"Current Gold Price: ${current_price:.2f}")
            # print(f"Predicted Price (30 min ahead): ${next_price:.2f}")
            # print(f"Predicted Change: ${predicted_change:.2f}")
            
            # print("\nDetailed Confidence Analysis:")
            # print(f"Success Rate (within 0.05% of actual): {self.confidence_metrics['success_rate_0.05']:.2f}%")
            # print(f"Success Rate (within 0.1% of actual): {self.confidence_metrics['success_rate_0.1']:.2f}%")
            # print(f"Success Rate (within 0.2% of actual): {self.confidence_metrics['success_rate_0.2']:.2f}%")
            # print(f"Average Percentage Error: {self.confidence_metrics['avg_percentage_error']:.2f}%")
            # print(f"95% Confidence Interval: ±${self.confidence_metrics['confidence_95']:.2f}")
            # print(f"99% Confidence Interval: ±${self.confidence_metrics['confidence_99']:.2f}")
            # print(f"Directional Accuracy: {self.confidence_metrics['directional_accuracy']:.2f}%")
            # print(f"Trend Accuracy: {self.confidence_metrics['trend_accuracy']:.2f}%")
            # print(f"Maximum Error: ${self.confidence_metrics['max_error']:.2f}")
            # print(f"Minimum Error: ${self.confidence_metrics['min_error']:.2f}")
            
            # print("\nTrading Signal (30-minute horizon):")
            # if predicted_change > 0:
            #     print(f"BUY - Expected Increase: ${predicted_change:.2f}")
            # elif predicted_change < 0:
            #     print(f"SELL - Expected Decrease: ${predicted_change:.2f}")
            # else:
            #     print("HOLD - No significant change expected")
            
            # Calculate and display prediction confidence
            confidence_score = (
                self.confidence_metrics['success_rate_0.1'] * 0.4 +
                self.confidence_metrics['directional_accuracy'] * 0.3 +
                self.confidence_metrics['trend_accuracy'] * 0.3
            )
            print(f"\nOverall Prediction Confidence M5: {confidence_score:.2f}%")
            
            # Show plot if requested
            if show_plot and y_test is not None and y_pred is not None:
                self.plot_predictions(y_test, y_pred)
            
            return (
                self.metrics,           # Dictionary of metrics
                current_price,          # Current gold price
                next_price,            # Predicted price (30 minutes ahead)
                predicted_change,       # Predicted change
                current_time_str,       # Current time
                predicted_time_str      # Predicted time (30 minutes ahead)
            )
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return {}, None, None, None, None, None

def main():
    # Create predictor instance (7 days maximum for 5-minute data)
    predictor = GoldPricePredictorM5(days=7)
    
    # Get all 6 return values
    metrics, current_price, next_price, predicted_change, current_time, predicted_time = predictor.predict(show_plot=True)
    
    # Print results if all values are available
    if all(v is not None for v in [metrics, current_price, next_price, predicted_change]):
        # print("\nTime Information:")
        # print(f"Data Start: {predictor.data_start}")
        # print(f"Data End: {predictor.data_end}")
        # print(f"Current Time: {current_time}")
        # print(f"Prediction Time (30 min ahead): {predicted_time}")
        
        # print("\nGold Price Prediction Results:")
        # print(f"Model Accuracy (R2): {metrics['r2']:.4f}")
        # print(f"Mean Squared Error: {metrics['mse']:.4f}")
        # print(f"Root Mean Squared Error: {metrics['rmse']:.4f}")
        # print(f"Current Gold Price: ${current_price:.2f}")
        # print(f"Predicted Price (30 min ahead): ${next_price:.2f}")
        # print(f"Predicted Change: ${predicted_change:.2f}")
        
        # print("\nDetailed Confidence Analysis:")
        # print(f"Success Rate (within 0.05% of actual): {predictor.confidence_metrics['success_rate_0.05']:.2f}%")
        # print(f"Success Rate (within 0.1% of actual): {predictor.confidence_metrics['success_rate_0.1']:.2f}%")
        # print(f"Success Rate (within 0.2% of actual): {predictor.confidence_metrics['success_rate_0.2']:.2f}%")
        # print(f"Average Percentage Error: {predictor.confidence_metrics['avg_percentage_error']:.2f}%")
        # print(f"95% Confidence Interval: ±${predictor.confidence_metrics['confidence_95']:.2f}")
        # print(f"99% Confidence Interval: ±${predictor.confidence_metrics['confidence_99']:.2f}")
        # print(f"Directional Accuracy: {predictor.confidence_metrics['directional_accuracy']:.2f}%")
        # print(f"Trend Accuracy: {predictor.confidence_metrics['trend_accuracy']:.2f}%")
        # print(f"Maximum Error: ${predictor.confidence_metrics['max_error']:.2f}")
        # print(f"Minimum Error: ${predictor.confidence_metrics['min_error']:.2f}")
        
        # print("\nTrading Signal (30-minute horizon):")
        # if predicted_change > 0:
        #     print(f"BUY - Expected Increase: ${predicted_change:.2f}")
        # elif predicted_change < 0:
        #     print(f"SELL - Expected Decrease: ${predicted_change:.2f}")
        # else:
        #     print("HOLD - No significant change expected")
        
        # Calculate and display prediction confidence
        confidence_score = (
            predictor.confidence_metrics['success_rate_0.1'] * 0.4 +
            predictor.confidence_metrics['directional_accuracy'] * 0.3 +
            predictor.confidence_metrics['trend_accuracy'] * 0.3
        )
        print(f"\nOverall Prediction Confidence M5: {confidence_score:.2f}%")

if __name__ == '__main__':
    main()


    