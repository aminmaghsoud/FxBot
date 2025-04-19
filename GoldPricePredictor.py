# Import required libraries
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

class GoldPricePredictor:
    def __init__(self, days: int = 30, test_size: float = 0.2, random_state: int = 42):
        """Initialize the Gold Price Predictor"""
        self.days = days
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

    def get_gold_data(self) -> Optional[pd.DataFrame]:
        """Get Gold price data using GLD ETF with hourly intervals"""
        try:
            symbol = "GLD"  # SPDR Gold Shares ETF
            end_date = datetime.now()
            start_date = end_date - timedelta(days=self.days)
            
            print(f"Downloading gold price data (GLD) from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
            df = yf.download(symbol, start=start_date, end=end_date, interval='1h')
            
            if df.empty:
                raise ValueError("No data was downloaded")
            
            # Handle MultiIndex columns if they exist
            if isinstance(df.columns, pd.MultiIndex):
                # Select the GLD ticker columns and flatten the MultiIndex
                df = df.xs('GLD', axis=1, level=1)
            
            # Convert GLD price to approximate gold price (1 GLD ≈ 1/10 oz of gold)
            for column in ['Open', 'High', 'Low', 'Close']:
                if column in df.columns:
                    df[column] = df[column] * 10
            
            print(f"Successfully downloaded {len(df)} data points")
            if 'Close' in df.columns:
                print(f"Latest gold price: ${float(df['Close'].iloc[-1]):.2f}")
            
            # Store data range information
            self.data_start = df.index[0].strftime('%Y-%m-%d %H:%M:%S')
            self.data_end = df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            self.df = df
            
            return df
        except Exception as e:
            print(f"Error downloading data: {str(e)}")
            print("Available columns:", df.columns if 'df' in locals() else "No data downloaded")
            return None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[pd.DataFrame]]:
        """Prepare data for training"""
        try:
            # Create features
            df['Hour'] = df.index.hour
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = df['Close'].pct_change()
            df['Volume_Change'] = df['Volume'].diff()
            df['High_Low_Diff'] = df['High'] - df['Low']
            df['MA_5'] = df['Close'].rolling(window=5).mean()
            
            # Create target (next hour's price)
            df['Target'] = df['Close'].shift(-1)
            
            # Remove NaN values
            df = df.dropna()
            
            # Features for prediction
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Hour',
                       'Price_Change', 'Price_Change_Pct', 'Volume_Change', 
                       'High_Low_Diff', 'MA_5']
            
            X = df[features]
            y = df['Target']
            
            return X, y, df
        except Exception as e:
            print(f"Error preparing data: {str(e)}")
            return None, None, None

    def train_model(self, X: pd.DataFrame, y: pd.Series) -> Tuple[Optional[LinearRegression], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[float], Optional[float]]:
        """Train the linear regression model"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
            
            # Train model
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store model and metrics
            self.model = model
            self.metrics = {
                'mse': mse,
                'r2': r2,
                'rmse': np.sqrt(mse)
            }
            
            return model, X_test, y_test, y_pred, mse, r2
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
        """Plot actual vs predicted prices"""
        try:
            plt.figure(figsize=(12, 6))
            sns.set_style('whitegrid')
            
            x_axis = range(len(y_test))
            plt.plot(x_axis, y_test, color='gold', label='Actual Gold Price', linewidth=2)
            plt.plot(x_axis, y_pred, '--', color='blue', label='Predicted Gold Price', linewidth=1.5)
            
            plt.title('Spot Gold Price Prediction (1-Hour Forecast)')
            plt.xlabel('Time (Hours)')
            plt.ylabel('Price (USD/oz)')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            if show_plot:
                plt.show(block=True)
        except Exception as e:
            print(f"Error plotting results: {str(e)}")

    def predict(self, show_plot: bool = True) -> Tuple[Dict[str, Any], Optional[float], Optional[float], Optional[float], Optional[str], Optional[str]]:
        """
        Run the complete prediction process and return results.
        
        Returns:
            Tuple containing:
            - metrics (Dict[str, Any]): Dictionary with 'mse', 'r2', and 'rmse'
            - current_price (float): Current gold price
            - next_price (float): Predicted next hour price
            - predicted_change (float): Predicted price change
            - current_time (str): Current price timestamp
            - predicted_time (str): Prediction timestamp (1 hour ahead)
        """
        # Get and validate data
        df = self.get_gold_data()
        if df is None:
            return {}, None, None, None, None, None
        
        # Prepare and validate data
        X, y, df_prepared = self.prepare_data(df)
        if X is None or y is None:
            return {}, None, None, None, None, None
        
        # Train model and validate
        model_results = self.train_model(X, y)
        if model_results[0] is None:
            return {}, None, None, None, None, None
        
        # Get prediction components
        model, X_test, y_test, y_pred, mse, r2 = model_results
        latest_data = X.iloc[-1].values
        next_hour_price = self.predict_next_hour(latest_data)
        current_price = df['Close'].iloc[-1].item()
        
        # Get timestamps
        current_time = df.index[-1]
        predicted_time = current_time + timedelta(hours=1)
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        predicted_time_str = predicted_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Store values
        self.current_price = current_price
        self.current_time = current_time_str
        self.predicted_time = predicted_time_str
        self.latest_data = latest_data
        
        # Calculate change
        predicted_change = next_hour_price - current_price if next_hour_price is not None else None
        
        # Show plot if requested
        if show_plot:
            self.plot_predictions(y_test, y_pred)
        
        # Return all 6 values
        return (
            self.metrics,           # Dictionary of metrics
            current_price,          # Current gold price
            next_hour_price,        # Predicted price
            predicted_change,       # Predicted change
            current_time_str,       # Current time
            predicted_time_str      # Predicted time
        )

def main():
    # Create predictor instance
    predictor = GoldPricePredictor(days=30)
    
    # Get all 6 return values
    metrics, current_price, next_price, predicted_change, current_time, predicted_time = predictor.predict(show_plot=True)
    
    # Print results if all values are available
    if all(v is not None for v in [metrics, current_price, next_price, predicted_change]):
        print("\nTime Information:")
        print(f"Data Start: {predictor.data_start}")
        print(f"Data End: {predictor.data_end}")
        print(f"Current Time: {current_time}")
        print(f"Prediction Time: {predicted_time}")
        
        print("\nSpot Gold Price Prediction Results:")
        print(f"Model Accuracy (R2): {metrics['r2']:.4f}")
        print(f"Mean Squared Error: {metrics['mse']:.4f}")
        print(f"Root Mean Squared Error: {metrics['rmse']:.4f}")
        print(f"Current Gold Price: ${current_price:.2f}")
        print(f"Predicted Price: ${next_price:.2f}")
        print(f"Predicted Change: ${predicted_change:.2f}")
        
        print("\nTrading Signal:")
        if predicted_change > 0:
            print(f"BUY - Expected Increase: ${predicted_change:.2f}")
        elif predicted_change < 0:
            print(f"SELL - Expected Decrease: ${predicted_change:.2f}")
        else:
            print("HOLD - No significant change expected")

if __name__ == '__main__':
    main()