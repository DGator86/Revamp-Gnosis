import pytest
import numpy as np
from app.services.indicators import TechnicalIndicatorService
import pandas as pd


class TestTechnicalIndicators:
    """Test technical indicator computations"""
    
    def setup_method(self):
        self.indicator_service = TechnicalIndicatorService()
        
        # Create sample data
        np.random.seed(42)
        n = 100
        self.prices = pd.Series(100 + np.cumsum(np.random.randn(n) * 2))
        
        self.df = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=n, freq='1min'),
            'open': self.prices + np.random.randn(n) * 0.5,
            'high': self.prices + np.abs(np.random.randn(n)) * 0.5,
            'low': self.prices - np.abs(np.random.randn(n)) * 0.5,
            'close': self.prices,
            'volume': np.random.randint(1000, 10000, n)
        })
    
    def test_compute_ewma(self):
        """Test EWMA computation"""
        ewma = self.indicator_service.compute_ewma(self.prices)
        
        assert len(ewma) == len(self.prices)
        assert not ewma.isna().all()
        assert ewma.iloc[-1] > 0
    
    def test_compute_vwap(self):
        """Test VWAP computation"""
        vwap = self.indicator_service.compute_vwap(self.df)
        
        assert len(vwap) == len(self.df)
        assert vwap.iloc[-1] > 0
        assert not vwap.isna().all()
    
    def test_compute_rsi(self):
        """Test RSI computation"""
        rsi = self.indicator_service.compute_rsi(self.prices)
        
        assert len(rsi) == len(self.prices)
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()
    
    def test_compute_bollinger_bands(self):
        """Test Bollinger Bands computation"""
        upper, middle, lower = self.indicator_service.compute_bollinger_bands(self.prices)
        
        assert len(upper) == len(self.prices)
        assert len(middle) == len(self.prices)
        assert len(lower) == len(self.prices)
        
        # Upper should be greater than middle, middle greater than lower
        valid_idx = ~(upper.isna() | middle.isna() | lower.isna())
        assert (upper[valid_idx] >= middle[valid_idx]).all()
        assert (middle[valid_idx] >= lower[valid_idx]).all()
    
    def test_compute_ichimoku(self):
        """Test Ichimoku Cloud computation"""
        ichimoku = self.indicator_service.compute_ichimoku(self.df)
        
        assert 'tenkan_sen' in ichimoku
        assert 'kijun_sen' in ichimoku
        assert 'senkou_span_a' in ichimoku
        assert 'senkou_span_b' in ichimoku
        assert 'chikou_span' in ichimoku
        
        assert len(ichimoku['tenkan_sen']) == len(self.df)
    
    def test_compute_all_indicators(self):
        """Test computing all indicators together"""
        result = self.indicator_service.compute_all_indicators(self.df)
        
        # Check all expected columns exist
        expected_cols = [
            'sigma_ewma', 'vwap', 'rsi',
            'bollinger_upper', 'bollinger_middle', 'bollinger_lower',
            'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b', 'chikou_span'
        ]
        
        for col in expected_cols:
            assert col in result.columns
