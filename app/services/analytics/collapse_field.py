import numpy as np
from typing import List, Tuple, Dict
from scipy import stats
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class CollapseFieldAnalytics:
    """
    Implements collapse-field analytics:
    - Pool field L(z) on z∈[-4,4] step 0.25
    - Particle A(t) tracking
    - Probabilistic dealer sign (p,q)
    - Hazard λ(t)
    - Forward map P(τ,z) with confidence horizon
    """
    
    def __init__(self):
        self.z_min = settings.z_min
        self.z_max = settings.z_max
        self.z_step = settings.z_step
        self.confidence_levels = settings.confidence_levels
        
        # Create z-grid for pool field
        self.z_values = np.arange(self.z_min, self.z_max + self.z_step, self.z_step)
    
    def compute_pool_field(
        self,
        returns: np.ndarray,
        prices: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute pool field L(z) over the z-grid
        
        L(z) represents the liquidity density at standardized price level z
        Uses kernel density estimation on standardized returns
        
        Args:
            returns: Array of price returns
            prices: Array of prices
            
        Returns:
            (z_values, L_values): z-grid and corresponding L(z) values
        """
        # Standardize returns to z-scores
        if len(returns) < 2:
            return self.z_values, np.zeros_like(self.z_values)
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return self.z_values, np.zeros_like(self.z_values)
        
        z_scores = (returns - mean_return) / std_return
        
        # Kernel density estimation for liquidity pool
        kde = stats.gaussian_kde(z_scores)
        L_values = kde(self.z_values)
        
        # Normalize to probability density
        L_values = L_values / np.sum(L_values)
        
        return self.z_values, L_values
    
    def compute_particle_state(
        self,
        current_price: float,
        prices: np.ndarray,
        timestamps: np.ndarray
    ) -> Tuple[float, float]:
        """
        Compute particle A(t) position and velocity
        
        The particle represents the current market state in the collapse field
        
        Args:
            current_price: Current market price
            prices: Historical prices
            timestamps: Corresponding timestamps (in seconds)
            
        Returns:
            (position, velocity): Particle position (z-score) and velocity
        """
        if len(prices) < 2:
            return 0.0, 0.0
        
        # Position: standardized current price
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        if std_price == 0:
            position = 0.0
        else:
            position = (current_price - mean_price) / std_price
        
        # Velocity: rate of change in z-space
        if len(prices) >= 2 and len(timestamps) >= 2:
            dt = timestamps[-1] - timestamps[-2]
            if dt > 0:
                z_prev = (prices[-2] - mean_price) / std_price if std_price > 0 else 0.0
                z_curr = position
                velocity = (z_curr - z_prev) / dt
            else:
                velocity = 0.0
        else:
            velocity = 0.0
        
        return float(position), float(velocity)
    
    def compute_dealer_probabilities(
        self,
        bid_sizes: np.ndarray,
        ask_sizes: np.ndarray,
        volumes: np.ndarray
    ) -> Tuple[float, float]:
        """
        Compute probabilistic dealer sign parameters (p, q)
        
        p: probability of dealer buying (absorbing selling pressure)
        q: probability of dealer selling (absorbing buying pressure)
        
        Args:
            bid_sizes: Array of bid sizes
            ask_sizes: Array of ask sizes
            volumes: Array of trade volumes
            
        Returns:
            (p, q): Dealer probability parameters
        """
        if len(bid_sizes) == 0 or len(ask_sizes) == 0:
            return 0.5, 0.5
        
        # Order flow imbalance
        total_bid = np.sum(bid_sizes)
        total_ask = np.sum(ask_sizes)
        total_flow = total_bid + total_ask
        
        if total_flow == 0:
            return 0.5, 0.5
        
        # p: probability dealer is on bid side (buying)
        # Higher when ask pressure is strong
        p = total_ask / total_flow
        
        # q: probability dealer is on ask side (selling)
        # Higher when bid pressure is strong
        q = total_bid / total_flow
        
        # Apply smoothing to avoid extreme values
        p = np.clip(p, 0.1, 0.9)
        q = np.clip(q, 0.1, 0.9)
        
        return float(p), float(q)
    
    def compute_hazard_rate(
        self,
        volatility: float,
        volume: float,
        avg_volume: float
    ) -> float:
        """
        Compute hazard rate λ(t)
        
        The hazard rate represents the instantaneous probability of a 
        regime change or market "collapse"
        
        Args:
            volatility: Current volatility estimate
            volume: Current volume
            avg_volume: Average volume
            
        Returns:
            lambda: Hazard rate
        """
        # Base hazard increases with volatility
        base_hazard = volatility
        
        # Volume factor: unusual volume increases hazard
        if avg_volume > 0:
            volume_factor = volume / avg_volume
            # Penalize both unusually high and low volume
            volume_adjustment = abs(np.log(volume_factor)) if volume_factor > 0 else 0
        else:
            volume_adjustment = 0
        
        # Combined hazard rate
        lambda_t = base_hazard * (1 + volume_adjustment)
        
        return float(lambda_t)
    
    def compute_forward_map(
        self,
        current_z: float,
        L_values: np.ndarray,
        lambda_t: float,
        tau_horizons: List[float] = None
    ) -> Tuple[List[float], List[List[float]], List[Dict]]:
        """
        Compute forward probability map P(τ,z) with confidence intervals
        
        Projects the probability distribution forward in time, accounting
        for hazard rate and pool field structure
        
        Args:
            current_z: Current particle position
            L_values: Pool field values L(z)
            lambda_t: Hazard rate
            tau_horizons: Time horizons for projection (in minutes)
            
        Returns:
            (tau_horizons, probability_maps, confidence_intervals)
        """
        if tau_horizons is None:
            tau_horizons = [1, 5, 15, 30, 60]  # minutes
        
        probability_maps = []
        confidence_intervals = []
        
        for tau in tau_horizons:
            # Diffusion with drift toward pool equilibrium
            # P(τ,z) ∝ exp(-λτ) * L(z) * G(z - current_z, σ²τ)
            
            # Time-dependent volatility
            sigma_tau = np.sqrt(tau / 60.0)  # Scale by hour
            
            # Gaussian kernel from current position
            gaussian = stats.norm.pdf(self.z_values, loc=current_z, scale=sigma_tau)
            
            # Combine with pool field and hazard decay
            P_tau_z = np.exp(-lambda_t * tau / 60.0) * L_values * gaussian
            
            # Normalize
            if np.sum(P_tau_z) > 0:
                P_tau_z = P_tau_z / np.sum(P_tau_z)
            
            probability_maps.append(P_tau_z.tolist())
            
            # Compute confidence intervals
            cdf = np.cumsum(P_tau_z)
            confidence = {}
            
            for level in self.confidence_levels:
                lower_idx = np.searchsorted(cdf, (1 - level) / 2)
                upper_idx = np.searchsorted(cdf, 1 - (1 - level) / 2)
                
                confidence[f'level_{level}'] = {
                    'lower_z': float(self.z_values[lower_idx]),
                    'upper_z': float(self.z_values[upper_idx]),
                    'tau': tau
                }
            
            confidence_intervals.append(confidence)
        
        return tau_horizons, probability_maps, confidence_intervals
    
    def compute_full_analytics(
        self,
        prices: np.ndarray,
        volumes: np.ndarray,
        timestamps: np.ndarray,
        bid_sizes: np.ndarray = None,
        ask_sizes: np.ndarray = None
    ) -> Dict:
        """
        Compute complete collapse field analytics
        
        Args:
            prices: Array of prices
            volumes: Array of volumes
            timestamps: Array of timestamps (seconds since epoch)
            bid_sizes: Optional array of bid sizes
            ask_sizes: Optional array of ask sizes
            
        Returns:
            Dictionary with all analytics components
        """
        # Compute returns
        returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
        
        # Pool field L(z)
        z_values, L_values = self.compute_pool_field(returns, prices)
        
        # Particle state A(t)
        current_price = prices[-1] if len(prices) > 0 else 0.0
        particle_position, particle_velocity = self.compute_particle_state(
            current_price, prices, timestamps
        )
        
        # Dealer probabilities (p, q)
        if bid_sizes is not None and ask_sizes is not None:
            dealer_p, dealer_q = self.compute_dealer_probabilities(
                bid_sizes, ask_sizes, volumes
            )
        else:
            dealer_p, dealer_q = 0.5, 0.5
        
        # Hazard rate λ(t)
        volatility = np.std(returns) if len(returns) > 0 else 0.0
        avg_volume = np.mean(volumes) if len(volumes) > 0 else 1.0
        current_volume = volumes[-1] if len(volumes) > 0 else 0.0
        hazard_lambda = self.compute_hazard_rate(volatility, current_volume, avg_volume)
        
        # Forward map P(τ,z)
        tau_horizons, probability_maps, confidence_intervals = self.compute_forward_map(
            particle_position, L_values, hazard_lambda
        )
        
        return {
            'pool_field_z_values': z_values.tolist(),
            'pool_field_l_values': L_values.tolist(),
            'particle_position': particle_position,
            'particle_velocity': particle_velocity,
            'dealer_prob_p': dealer_p,
            'dealer_prob_q': dealer_q,
            'hazard_lambda': hazard_lambda,
            'forward_map_tau': tau_horizons,
            'forward_map_prob': probability_maps,
            'confidence_levels': confidence_intervals
        }
