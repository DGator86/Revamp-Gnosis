import pytest
import numpy as np
from app.services.analytics import CollapseFieldAnalytics


class TestCollapseField:
    """Test collapse field analytics computations"""
    
    def setup_method(self):
        self.analytics = CollapseFieldAnalytics()
        
        # Create sample data
        np.random.seed(42)
        n = 100
        self.prices = 100 + np.cumsum(np.random.randn(n) * 2)
        self.volumes = np.random.randint(1000, 10000, n)
        self.timestamps = np.arange(n) * 60  # 1-minute intervals
        self.bid_sizes = np.random.randint(100, 1000, n)
        self.ask_sizes = np.random.randint(100, 1000, n)
    
    def test_compute_pool_field(self):
        """Test pool field L(z) computation"""
        returns = np.diff(self.prices) / self.prices[:-1]
        z_values, L_values = self.analytics.compute_pool_field(returns, self.prices)
        
        assert len(z_values) == len(L_values)
        assert len(z_values) > 0
        # L(z) should be normalized (sum to ~1)
        assert abs(np.sum(L_values) - 1.0) < 0.01
        # All L values should be non-negative
        assert (L_values >= 0).all()
    
    def test_compute_particle_state(self):
        """Test particle A(t) state computation"""
        position, velocity = self.analytics.compute_particle_state(
            self.prices[-1], self.prices, self.timestamps
        )
        
        assert isinstance(position, float)
        assert isinstance(velocity, float)
        # Position should be a reasonable z-score
        assert -10 < position < 10
    
    def test_compute_dealer_probabilities(self):
        """Test probabilistic dealer sign (p,q) computation"""
        p, q = self.analytics.compute_dealer_probabilities(
            self.bid_sizes, self.ask_sizes, self.volumes
        )
        
        assert isinstance(p, float)
        assert isinstance(q, float)
        # Probabilities should be between 0 and 1
        assert 0 <= p <= 1
        assert 0 <= q <= 1
        # p + q should be close to 1 (by construction)
        assert abs(p + q - 1.0) < 0.01
    
    def test_compute_hazard_rate(self):
        """Test hazard rate λ(t) computation"""
        volatility = 0.02
        volume = 5000
        avg_volume = 4000
        
        lambda_t = self.analytics.compute_hazard_rate(volatility, volume, avg_volume)
        
        assert isinstance(lambda_t, float)
        assert lambda_t >= 0
    
    def test_compute_forward_map(self):
        """Test forward map P(τ,z) computation"""
        returns = np.diff(self.prices) / self.prices[:-1]
        z_values, L_values = self.analytics.compute_pool_field(returns, self.prices)
        current_z = 0.5
        lambda_t = 0.1
        
        tau_horizons, probability_maps, confidence_intervals = self.analytics.compute_forward_map(
            current_z, L_values, lambda_t
        )
        
        assert len(tau_horizons) > 0
        assert len(probability_maps) == len(tau_horizons)
        assert len(confidence_intervals) == len(tau_horizons)
        
        # Check probability maps are normalized
        for prob_map in probability_maps:
            assert abs(np.sum(prob_map) - 1.0) < 0.01
        
        # Check confidence intervals
        for ci in confidence_intervals:
            for level_key in ci.keys():
                assert 'lower_z' in ci[level_key]
                assert 'upper_z' in ci[level_key]
                assert 'tau' in ci[level_key]
    
    def test_compute_full_analytics(self):
        """Test complete analytics computation"""
        result = self.analytics.compute_full_analytics(
            self.prices, self.volumes, self.timestamps,
            self.bid_sizes, self.ask_sizes
        )
        
        # Check all expected keys exist
        expected_keys = [
            'pool_field_z_values', 'pool_field_l_values',
            'particle_position', 'particle_velocity',
            'dealer_prob_p', 'dealer_prob_q',
            'hazard_lambda',
            'forward_map_tau', 'forward_map_prob', 'confidence_levels'
        ]
        
        for key in expected_keys:
            assert key in result
        
        # Validate data types and ranges
        assert isinstance(result['pool_field_z_values'], list)
        assert isinstance(result['pool_field_l_values'], list)
        assert len(result['pool_field_z_values']) == len(result['pool_field_l_values'])
        
        assert isinstance(result['particle_position'], float)
        assert isinstance(result['particle_velocity'], float)
        
        assert 0 <= result['dealer_prob_p'] <= 1
        assert 0 <= result['dealer_prob_q'] <= 1
        
        assert result['hazard_lambda'] >= 0
        
        assert len(result['forward_map_tau']) > 0
        assert len(result['forward_map_prob']) == len(result['forward_map_tau'])
