import pandas as pd
import numpy as np
from typing import List, Tuple
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicatorService:
    """Computes technical indicators: EWMA, VWAP, RSI, Bollinger, Ichimoku"""
    
    def __init__(self):
        self.ewma_span = settings.ewma_span
        self.rsi_period = settings.rsi_period
        self.bollinger_period = settings.bollinger_period
        self.bollinger_std = settings.bollinger_std
    
    def compute_ewma(self, prices: pd.Series) -> pd.Series:
        """Compute Exponentially Weighted Moving Average (Sigma)"""
        return prices.ewm(span=self.ewma_span, adjust=False).mean()
    
    def compute_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Compute Volume Weighted Average Price
        df must have columns: high, low, close, volume
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    def compute_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """Compute Relative Strength Index"""
        if period is None:
            period = self.rsi_period
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def compute_bollinger_bands(
        self,
        prices: pd.Series,
        period: int = None,
        num_std: float = None
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Compute Bollinger Bands
        Returns: (upper, middle, lower)
        """
        if period is None:
            period = self.bollinger_period
        if num_std is None:
            num_std = self.bollinger_std
        
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * num_std)
        lower = middle - (std * num_std)
        
        return upper, middle, lower
    
    def compute_ichimoku(
        self,
        df: pd.DataFrame,
        tenkan_period: int = 9,
        kijun_period: int = 26,
        senkou_b_period: int = 52
    ) -> dict:
        """
        Compute Ichimoku Cloud components (optimized for 15-minute timeframe)
        df must have columns: high, low, close
        
        Returns dict with:
        - tenkan_sen (Conversion Line)
        - kijun_sen (Base Line)
        - senkou_span_a (Leading Span A)
        - senkou_span_b (Leading Span B)
        - chikou_span (Lagging Span)
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        tenkan_sen = (high.rolling(window=tenkan_period).max() + 
                      low.rolling(window=tenkan_period).min()) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        kijun_sen = (high.rolling(window=kijun_period).max() + 
                     low.rolling(window=kijun_period).min()) / 2
        
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low) / 2
        senkou_span_b = ((high.rolling(window=senkou_b_period).max() + 
                          low.rolling(window=senkou_b_period).min()) / 2).shift(kijun_period)
        
        # Chikou Span (Lagging Span): Close shifted back 26 periods
        chikou_span = close.shift(-kijun_period)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    def compute_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all technical indicators for a DataFrame of market data
        df must have columns: timestamp, open, high, low, close, volume
        """
        result = df.copy()
        
        # EWMA (Sigma)
        result['sigma_ewma'] = self.compute_ewma(df['close'])
        
        # VWAP
        result['vwap'] = self.compute_vwap(df)
        
        # RSI
        result['rsi'] = self.compute_rsi(df['close'])
        
        # Bollinger Bands
        upper, middle, lower = self.compute_bollinger_bands(df['close'])
        result['bollinger_upper'] = upper
        result['bollinger_middle'] = middle
        result['bollinger_lower'] = lower
        
        # Ichimoku (if we have enough data)
        if len(df) >= 52:
            ichimoku = self.compute_ichimoku(df)
            result['tenkan_sen'] = ichimoku['tenkan_sen']
            result['kijun_sen'] = ichimoku['kijun_sen']
            result['senkou_span_a'] = ichimoku['senkou_span_a']
            result['senkou_span_b'] = ichimoku['senkou_span_b']
            result['chikou_span'] = ichimoku['chikou_span']
        
        return result
