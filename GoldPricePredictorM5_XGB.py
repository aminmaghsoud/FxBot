import MetaTrader5 as MT5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import seaborn as sns

class GoldPricePredictorM5_XGB:
    def __init__(self, pair, days: int = 7, test_size: float = 0.2, random_state: int = 42):
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
        self.confidence_metrics = {}
        self.scaler = StandardScaler()

    def get_gold_data(self) -> Optional[pd.DataFrame]:
        try:
            if not MT5.initialize():
                raise RuntimeError("MT5 initialization failed")

            rates = MT5.copy_rates_from_pos(self.Pair, MT5.TIMEFRAME_M5, 0, 2500)
            if rates is None:
                raise ValueError("Failed to fetch data from MT5")

            df = pd.DataFrame(rates)
            if df.empty:
                raise ValueError("DataFrame is empty")

            df['datetime'] = pd.to_datetime(df['time'], unit='s')
            df.set_index(pd.DatetimeIndex(df['datetime']), inplace=True, drop=True)
            df.drop(columns=['time'], inplace=True)
            df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'tick_volume': 'Volume'
            }, inplace=True)

            self.df = df
            self.data_start = df.index[0].strftime('%Y-%m-%d %H:%M:%S')
            self.data_end = df.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            self.current_price = df['Close'].iloc[-1]

            return df
        except Exception as e:
            print(f"Error in get_gold_data: {e}")
            return None

    def prepare_data(self, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.Series], Optional[pd.DataFrame]]:
        try:
            df['Hour'] = df.index.hour
            df['Minute'] = df.index.minute
            df['DayOfWeek'] = df.index.dayofweek
            df['IsWeekend'] = df['DayOfWeek'].isin([5, 6]).astype(int)
            df['Price_Change'] = df['Close'].diff()
            df['Price_Change_Pct'] = df['Close'].pct_change()
            df['Volume_Change'] = df['Volume'].diff()
            df['High_Low_Diff'] = df['High'] - df['Low']
            df['MA_5'] = df['Close'].rolling(window=5).mean()
            df['MA_12'] = df['Close'].rolling(window=12).mean()
            df['MA_30'] = df['Close'].rolling(window=30).mean()
            df['MA_72'] = df['Close'].rolling(window=72).mean()
            df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
            df['Momentum_12'] = df['Close'] - df['Close'].shift(12)
            df['Volatility_5'] = df['Close'].rolling(window=5).std()
            df['Volatility_12'] = df['Close'].rolling(window=12).std()
            df['Target'] = df['Close'].shift(-6)
            df = df.dropna()

            features = [
                'Open', 'High', 'Low', 'Close', 'Volume',
                'Hour', 'Minute', 'DayOfWeek', 'IsWeekend',
                'Price_Change', 'Price_Change_Pct', 'Volume_Change',
                'High_Low_Diff', 'MA_5', 'MA_12', 'MA_30', 'MA_72',
                'Momentum_5', 'Momentum_12', 'Volatility_5', 'Volatility_12'
            ]

            X = df[features]
            y = df['Target']
            return X, y, df
        except Exception as e:
            print(f"Error preparing data: {e}")
            return None, None, None

    def calculate_confidence_metrics(self, y_test: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        try:
            errors = np.abs(y_test - y_pred)
            percentage_errors = (errors / y_test) * 100
            
            thresholds = [0.05, 0.1, 0.2]
            success_rates = {}
            for threshold in thresholds:
                successful_predictions = np.sum(percentage_errors <= threshold)
                success_rates[f'success_rate_{threshold}'] = (successful_predictions / len(y_test)) * 100
            
            std_error = np.std(errors)
            confidence_95 = 1.96 * std_error
            confidence_99 = 2.58 * std_error
            
            if len(y_test) > 1 and len(y_pred) > 1:
                actual_changes = np.diff(y_test)
                predicted_changes = np.diff(y_pred)
                directional_accuracy = np.mean(np.sign(actual_changes) == np.sign(predicted_changes)) * 100
            else:
                directional_accuracy = 0.0
            
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

    def train_model(self, X: pd.DataFrame, y: pd.Series):
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.test_size, random_state=self.random_state)
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('xgb_model', XGBRegressor(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=self.random_state
                ))
            ])
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            self.model = pipeline
            self.metrics = {'mse': mse, 'r2': r2, 'rmse': np.sqrt(mse)}
            self.confidence_metrics = self.calculate_confidence_metrics(y_test, y_pred)

            feature_importance = pd.DataFrame({
                'Feature': X.columns,
                'Importance': pipeline.named_steps['xgb_model'].feature_importances_
            }).sort_values(by='Importance', ascending=False)

            return pipeline, X_test, y_test, y_pred, mse, r2
        except Exception as e:
            print(f"Error training model: {e}")
            return None, None, None, None, None, None

    def plot_predictions(self, y_test: np.ndarray, y_pred: np.ndarray, show_plot: bool = True) -> None:
        try:
            plt.figure(figsize=(12, 6))
            sns.set_style('whitegrid')
            
            x_axis = range(len(y_test))
            plt.plot(x_axis, y_test, color='gold', label='Actual Gold Price', linewidth=2)
            plt.plot(x_axis, y_pred, '--', color='blue', label='Predicted Gold Price', linewidth=1.5)
            
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

    def predict(self, show_plot: bool = True) -> Tuple[Dict[str, Any], float, float, float, str, str]:
        try:
            df = self.get_gold_data()
            if df is None:
                print("Error: Could not get gold data")
                return {}, 0, 0, 0, '', ''
            
            X, y, df_prepared = self.prepare_data(df)
            if X is None or y is None:
                print("Error: Could not prepare data")
                return {}, 0, 0, 0, '', ''
            
            self.model, X_test, y_test, y_pred, mse, r2 = self.train_model(X, y)
            if self.model is None:
                print("Error: Could not train model")
                return {}, 0, 0, 0, '', ''
            
            latest_data = X.iloc[-1:].values
            next_price = float(self.model.predict(latest_data)[0])
            current_price = df['Close'].iloc[-1]
            
            current_time = df.index[-1]
            predicted_time = current_time + timedelta(minutes=30)
            current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            predicted_time_str = predicted_time.strftime('%Y-%m-%d %H:%M:%S')
            
            self.current_price = current_price
            self.current_time = current_time_str
            self.predicted_time = predicted_time_str
            self.latest_data = latest_data
            
            predicted_change = next_price - current_price
            
            if show_plot and y_test is not None and y_pred is not None:
                self.plot_predictions(y_test, y_pred)
            
            return (
                self.metrics,
                current_price,
                next_price,
                predicted_change,
                current_time_str,
                predicted_time_str
            )
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return {}, 0, 0, 0, '', ''

def main():
    predictor = GoldPricePredictorM5_XGB(pair='XAUUSDb')
    metrics, current_price, next_price, predicted_change, current_time, predicted_time = predictor.predict(show_plot=True)
    
    if all(v is not None for v in [metrics, current_price, next_price, predicted_change]):
        confidence_score = (
            predictor.confidence_metrics['success_rate_0.1'] * 0.4 +
            predictor.confidence_metrics['directional_accuracy'] * 0.3 +
            predictor.confidence_metrics['trend_accuracy'] * 0.3
        )
        print(f"\nOverall Prediction Confidence XGB: {confidence_score:.2f}%")

if __name__ == '__main__':
    main()
