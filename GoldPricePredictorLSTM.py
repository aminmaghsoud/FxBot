import numpy as np
import pandas as pd
import MetaTrader5 as MT5
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from datetime import timedelta

class GoldPricePredictorLSTM:
    def __init__(self, pair='XAUUSDb', timeframe=MT5.TIMEFRAME_H1, window_size=60, forecast_horizon=3):
        self.pair = pair
        self.timeframe = timeframe
        self.window_size = window_size
        self.forecast_horizon = forecast_horizon
        self.scaler = MinMaxScaler()
        self.model = None

    def fetch_data(self, n_bars=2000):
        if not MT5.initialize():
            raise RuntimeError("MT5 initialization failed")

        rates = MT5.copy_rates_from_pos(self.pair, self.timeframe, 0, n_bars)
        if rates is None:
            raise ValueError("No data retrieved from MT5")

        df = pd.DataFrame(rates)
        df['datetime'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('datetime', inplace=True)
        df.rename(columns={'close': 'Close'}, inplace=True)
        return df[['Close']]

    def prepare_data(self, df):
        scaled = self.scaler.fit_transform(df)
        X, y = [], []
        for i in range(self.window_size, len(scaled) - self.forecast_horizon):
            X.append(scaled[i - self.window_size:i])
            y.append(scaled[i + self.forecast_horizon][0])
        return np.array(X), np.array(y)

    def build_model(self):
        model = Sequential()
        model.add(LSTM(64, return_sequences=True, input_shape=(self.window_size, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(32))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        self.model = model

    def train(self, X, y, epochs=20, batch_size=32):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict_next(self, df):
        last_seq = self.scaler.transform(df[-self.window_size:].values)
        X_pred = np.expand_dims(last_seq, axis=0)
        scaled_pred = self.model.predict(X_pred)[0][0]
        return self.scaler.inverse_transform([[scaled_pred]])[0][0]

    def run(self):
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
