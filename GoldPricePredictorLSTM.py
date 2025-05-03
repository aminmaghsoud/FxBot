import numpy as np
import pandas as pd
import MetaTrader5 as MT5
from sklearn.preprocessing import RobustScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from datetime import timedelta
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

class GoldPricePredictorLSTM:
    def __init__(self, pair, timeframe=MT5.TIMEFRAME_H1, window_size=30, forecast_horizon=3):
        self.pair = pair
        self.timeframe = timeframe
        self.window_size = window_size  # Reduced from 60 to 30
        self.forecast_horizon = forecast_horizon
        self.scaler = RobustScaler()
        self.model = None
        self.price_scaler = RobustScaler()  # Separate scaler for price

    def fetch_data(self, n_bars=2000):
        if not MT5.initialize():
            raise RuntimeError("MT5 initialization failed")

        rates = MT5.copy_rates_from_pos(self.pair, self.timeframe, 0, n_bars)
        if rates is None:
            raise ValueError("No data retrieved from MT5")

        df = pd.DataFrame(rates)
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('datetime', inplace=True)
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'tick_volume': 'Volume'
        }, inplace=True)
        return df

    def add_technical_indicators(self, df):
        # Price-based indicators
        df['Price_Change'] = df['Close'].diff()
        df['Price_Change_Pct'] = df['Close'].pct_change()
        df['High_Low_Diff'] = df['High'] - df['Low']
        
        # Volume-based indicators
        df['Volume_Change'] = df['Volume'].diff()
        df['Volume_MA5'] = df['Volume'].rolling(window=5).mean()
        
        # RSI with different periods
        df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
        df['RSI_7'] = RSIIndicator(close=df['Close'], window=7).rsi()
        
        # MACD with standard parameters
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # Bollinger Bands with different periods
        bb_20 = BollingerBands(close=df['Close'], window=20)
        df['BB_Upper_20'] = bb_20.bollinger_hband()
        df['BB_Lower_20'] = bb_20.bollinger_lband()
        df['BB_Middle_20'] = bb_20.bollinger_mavg()
        
        bb_50 = BollingerBands(close=df['Close'], window=50)
        df['BB_Upper_50'] = bb_50.bollinger_hband()
        df['BB_Lower_50'] = bb_50.bollinger_lband()
        
        # Price position relative to Bollinger Bands
        df['BB_Position_20'] = (df['Close'] - df['BB_Lower_20']) / (df['BB_Upper_20'] - df['BB_Lower_20'])
        df['BB_Position_50'] = (df['Close'] - df['BB_Lower_50']) / (df['BB_Upper_50'] - df['BB_Lower_50'])
        
        # Remove any remaining NaN values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df

    def prepare_data(self, df):
        # Add technical indicators
        df = self.add_technical_indicators(df)
        
        # Select features for scaling
        features = [
            'Close', 'Volume', 'Price_Change', 'Price_Change_Pct',
            'High_Low_Diff', 'Volume_Change', 'Volume_MA5',
            'RSI_14', 'RSI_7', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'BB_Upper_20', 'BB_Lower_20', 'BB_Middle_20',
            'BB_Upper_50', 'BB_Lower_50',
            'BB_Position_20', 'BB_Position_50'
        ]
        
        # Scale features
        scaled_features = self.scaler.fit_transform(df[features])
        
        # Scale price separately
        scaled_price = self.price_scaler.fit_transform(df[['Close']])
        
        # Prepare sequences
        X, y = [], []
        for i in range(self.window_size, len(scaled_features) - self.forecast_horizon):
            X.append(scaled_features[i - self.window_size:i])
            y.append(scaled_price[i + self.forecast_horizon][0])
        
        return np.array(X), np.array(y)

    def build_model(self):
        model = Sequential()
        
        # First LSTM layer
        model.add(LSTM(32, return_sequences=True, input_shape=(self.window_size, 19)))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))
        
        # Second LSTM layer
        model.add(LSTM(16, return_sequences=True))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))
        
        # Third LSTM layer
        model.add(LSTM(8))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))
        
        # Output layer
        model.add(Dense(1))
        
        # Compile with adjusted learning rate
        optimizer = Adam(learning_rate=0.0005)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        
        self.model = model

    def train(self, X, y, epochs=100, batch_size=32):
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.00001
        )
        
        self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )

    def predict_next(self, df):
        # Add technical indicators to the last window
        df = self.add_technical_indicators(df)
        
        # Select features for scaling
        features = [
            'Close', 'Volume', 'Price_Change', 'Price_Change_Pct',
            'High_Low_Diff', 'Volume_Change', 'Volume_MA5',
            'RSI_14', 'RSI_7', 'MACD', 'MACD_Signal', 'MACD_Hist',
            'BB_Upper_20', 'BB_Lower_20', 'BB_Middle_20',
            'BB_Upper_50', 'BB_Lower_50',
            'BB_Position_20', 'BB_Position_50'
        ]
        
        # Scale features
        last_seq = self.scaler.transform(df[-self.window_size:][features])
        X_pred = np.expand_dims(last_seq, axis=0)
        
        # Make prediction
        scaled_pred = self.model.predict(X_pred)[0][0]
        return self.price_scaler.inverse_transform([[scaled_pred]])[0][0]

    def run(self):
        try:
            df = self.fetch_data()
            X, y = self.prepare_data(df)
            self.build_model()
            self.train(X, y)
            prediction = self.predict_next(df)
            current_price = df['Close'].iloc[-1]
            predicted_change = prediction - current_price
            predicted_time = df.index[-1] + timedelta(hours=self.forecast_horizon)

            print(f"Current Price: {current_price:.2f}")
            print(f"Predicted Price in {self.forecast_horizon} hours: {prediction:.2f}")
            print(f"Predicted Change: {predicted_change:.2f}")
            print(f"Predicted Time: {predicted_time}")
            
        except Exception as e:
            print(f"Error in GoldPricePredictorLSTM: {str(e)}")
