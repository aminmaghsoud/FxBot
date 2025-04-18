import unittest
import pandas as pd
import numpy as np
from SupplyDemandStrategyV1 import train_trend_model, calculate_technical_indicators

class TestTrendModel(unittest.TestCase):
    def setUp(self):
        # ایجاد داده‌های نمونه
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        self.sample_data = pd.DataFrame({
            'open': np.random.uniform(100, 200, 100),
            'high': np.random.uniform(200, 300, 100),
            'low': np.random.uniform(50, 100, 100),
            'close': np.random.uniform(100, 200, 100),
            'volume': np.random.uniform(1000, 5000, 100)
        }, index=dates)

    def test_technical_indicators(self):
        """تست محاسبه شاخص‌های تکنیکال"""
        df = calculate_technical_indicators(self.sample_data)
        required_columns = [
            'sma_20', 'ema_50', 'rsi', 'macd', 'macd_signal',
            'bb_bbm', 'bb_bbh', 'bb_bbl', 'adx', 'stochastic',
            'volume_ma', 'price_range', 'price_momentum'
        ]
        for col in required_columns:
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].isnull().all())

    def test_model_training(self):
        """تست آموزش مدل"""
        prediction, model = train_trend_model(self.sample_data)
        self.assertIsNotNone(prediction)
        self.assertIsNotNone(model)
        self.assertIn(prediction, [0, 1, 2])  # پیش‌بینی باید یکی از این مقادیر باشد

    def test_model_saving_loading(self):
        """تست ذخیره و بارگذاری مدل"""
        # آموزش و ذخیره مدل
        prediction, model = train_trend_model(self.sample_data, pair='TEST')
        
        # بارگذاری مجدد مدل
        loaded_prediction, loaded_model = train_trend_model(self.sample_data, pair='TEST')
        
        self.assertEqual(prediction, loaded_prediction)

if __name__ == '__main__':
    unittest.main() 