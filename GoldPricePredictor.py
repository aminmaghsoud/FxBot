import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
import MetaTrader5 as MT5
import xgboost as xgb
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange


class GoldPricePredictor:
    def __init__(
        self, 
        pair: str = 'XAUUSDb',
        days: int = 30,
        test_size: float = 0.2,
        random_state: int = 42,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        min_child_weight: int = 1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8
    ):
        """Initialize the Gold Price Predictor with XGBoost"""
        self.Pair = pair
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
        
        # XGBoost parameters
        self.xgb_params = {
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'min_child_weight': min_child_weight,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'objective': 'reg:squarederror',
            'random_state': random_state,
            'eval_metric': 'rmse'
        }

    def get_gold_data(self) -> Optional[pd.DataFrame]:
        """Get currency pair data from MetaTrader 5 (1-hour timeframe)"""
        try:
            if not MT5.initialize():
                raise RuntimeError("MT5 initialization failed")

            # Get symbol info to validate the pair
            symbol_info = MT5.symbol_info(self.Pair)
            if symbol_info is None:
                raise ValueError(f"Symbol {self.Pair} not found in MT5")

            RatesH1 = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_H1, 0, 2000)
            if RatesH1 is None:
                raise ValueError(f"Failed to fetch data for {self.Pair} from MT5")

            FrameRatesH1 = pd.DataFrame(RatesH1)
            if FrameRatesH1.empty:
                raise ValueError(f"DataFrame is empty for {self.Pair}")

            FrameRatesH1['datetime'] = pd.to_datetime(FrameRatesH1['time'], unit='s')
            FrameRatesH1.set_index(pd.DatetimeIndex(FrameRatesH1['datetime']), inplace=True, drop=True)
            FrameRatesH1.drop(columns=['time'], inplace=True)

            FrameRatesH1.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)

            self.df = FrameRatesH1
            self.data_start = FrameRatesH1.index[0].strftime('%Y-%m-%d %H:%M:%S')
            self.data_end = FrameRatesH1.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            self.current_price = FrameRatesH1['Close'].iloc[-1]

            return FrameRatesH1

        except Exception as e:
            print(f"Error in get_gold_data for {self.Pair}: {e}")
            return None

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        # Moving Averages
        df['SMA_5'] = SMAIndicator(close=df['Close'], window=5).sma_indicator()
        df['SMA_20'] = SMAIndicator(close=df['Close'], window=20).sma_indicator()
        df['EMA_12'] = EMAIndicator(close=df['Close'], window=12).ema_indicator()
        df['EMA_26'] = EMAIndicator(close=df['Close'], window=26).ema_indicator()
        
        # MACD
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # RSI
        df['RSI'] = RSIIndicator(close=df['Close']).rsi()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['Close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Middle'] = bb.bollinger_mavg()
        
        # ATR
        df['ATR'] = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close']).average_true_range()
        
        return df

    def prepare_data(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[pd.DataFrame]]:
        """Prepare data for training"""
        try:
            # Add technical indicators
            df = self.add_technical_indicators(df)
            
            # Create additional features
            df['Hour'] = df.index.hour
            df['Day_of_Week'] = df.index.dayofweek
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = df['Close'].pct_change()
            df['Volume_Change'] = df['Volume'].diff()
            df['High_Low_Diff'] = df['High'] - df['Low']
            
            # Create target (next hour's price)
            df['Target'] = df['Close'].shift(-3)

            # prediction_horizon = 3  # مثلاً پیش‌بینی 3 ساعت بعد
            # df['Target'] = df['Close'].shift(-prediction_horizon) - df['Close']  # پیش‌بینی Δ قیمت

            
            # Remove NaN values
            df = df.dropna()
            
            # Features for prediction
            features = [
                'Open', 'High', 'Low', 'Close', 'Volume',
                'Hour', 'Day_of_Week',
                'Price_Change', 'Price_Change_Pct', 'Volume_Change',
                'High_Low_Diff',
                'SMA_5', 'SMA_20', 'EMA_12', 'EMA_26',
                'MACD', 'MACD_Signal', 'MACD_Hist',
                'RSI', 'Stoch_K', 'Stoch_D',
                'BB_Upper', 'BB_Lower', 'BB_Middle',
                'ATR'
            ]
            
            X = df[features]
            y = df['Target']
            
            return X, y, df
        except Exception as e:
            print(f"Error preparing data: {str(e)}")
            return None, None, None

    def train_model(self, X: pd.DataFrame, y: pd.Series) -> Tuple[Optional[xgb.XGBRegressor], Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray], Optional[float], Optional[float]]:
        """Train the XGBoost model"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size, random_state=self.random_state
            )
            
            # Train model
            model = xgb.XGBRegressor(**self.xgb_params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Store model and metrics
            self.model = model
            self.metrics = {
                'mse': mse,
                'r2': r2,
                'rmse': np.sqrt(mse),
                'mae': mae
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
            plt.figure(figsize=(15, 8))
            sns.set_style('whitegrid')
            
            x_axis = range(len(y_test))
            plt.plot(x_axis, y_test, color='gold', label=f'Actual {self.Pair} Price', linewidth=2)
            plt.plot(x_axis, y_pred, '--', color='blue', label='Predicted Price', linewidth=1.5)
            
            plt.title(f'{self.Pair} Price Prediction (1-Hour Forecast)')
            plt.xlabel('Time (Hours)')
            plt.ylabel('Price')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            if show_plot:
                plt.show(block=True)
        except Exception as e:
            print(f"Error plotting results for {self.Pair}: {str(e)}")

    def predict(self, show_plot: bool = True) -> Tuple[Dict[str, Any], Optional[float], Optional[float], Optional[float], Optional[str], Optional[str]]:
        """
        Run the complete prediction process and return results.
        
        Returns:
            Tuple containing:
            - metrics (Dict[str, Any]): Dictionary with 'mse', 'r2', 'rmse', and 'mae'
            - current_price (float): Current price
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
        # predicted_change = model.predict(latest_data.reshape(1, -1))[0]
        # next_hour_price = current_price + predicted_change

        
        # Show plot if requested
        if show_plot:
            self.plot_predictions(y_test, y_pred)
        
        return (
            self.metrics,           # Dictionary of metrics
            current_price,          # Current price
            next_hour_price,        # Predicted price
            predicted_change,       # Predicted change
            current_time_str,       # Current time
            predicted_time_str      # Predicted time
        )

def main():
    # Create predictor instance with custom parameters
    predictor = GoldPricePredictor(
        pair='XAUUSDb',
        days=30,
        n_estimators=200,
        max_depth=8,
        learning_rate=0.05,
        min_child_weight=3,
        subsample=0.9,
        colsample_bytree=0.9
    )
    
    # Get all 6 return values
    metrics, current_price, next_price, predicted_change, current_time, predicted_time = predictor.predict(show_plot=True)
    
    # Print results if all values are available
    if all(v is not None for v in [metrics, current_price, next_price, predicted_change]):
        print("\nTime Information:")
        print(f"Data Start: {predictor.data_start}")
        print(f"Data End: {predictor.data_end}")
        print(f"Current Time: {current_time}")
        print(f"Predicted Time: {predicted_time}")
        
        print("\nGold Price Prediction Results:")
        print(f"Model Accuracy (R2): {metrics['r2']:.4f}")
        print(f"Mean Squared Error: {metrics['mse']:.4f}")
        print(f"Root Mean Squared Error: {metrics['rmse']:.4f}")
        print(f"Mean Absolute Error: {metrics['mae']:.4f}")
        print(f"Current Gold Price: ${current_price:.2f}")
        print(f"Predicted Gold Price: ${next_price:.2f}")
        print(f"Predicted Price Change: ${predicted_change:.2f}")
        
        print("\nTrading Signal:")
        if predicted_change > 0:
            print(f"Buy - Predicted Price Increase: ${predicted_change:.2f}")
        elif predicted_change < 0:
            print(f"Sell - Predicted Price Decrease: ${predicted_change:.2f}")
        else:
            print("Hold - No significant price change predicted")

if __name__ == '__main__':
    main()