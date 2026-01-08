import numpy as np
from app.config import settings

class LiquidityField:
    def __init__(self):
        self.z_grid = np.arange(settings.sigma_grid['min'], settings.sigma_grid['max'] + 0.125, settings.sigma_grid['step'])
        self.weights = settings.liquidity['weights']
        
    def gaussian_kernel(self, u, bandwidth):
        return np.exp(-0.5 * (u / bandwidth)**2)
        
    def compute_field(self, current_log_price, sigma, components):
        L_total = np.zeros_like(self.z_grid)
        
        if 'vwap' in components:
            l_vwap = np.zeros_like(self.z_grid)
            z_c = (np.log(components['vwap']['price']) - current_log_price) / sigma
            l_vwap += 1.0 * self.gaussian_kernel(self.z_grid - z_c, 0.35)
            L_total += self.weights['vwap'] * l_vwap

        if 'bb' in components:
            l_bb = np.zeros_like(self.z_grid)
            bb = components['bb']
            for val, w in [(bb['mb'], 1.0), (bb['ub'], 0.7), (bb['lb'], 0.7)]:
                z = (np.log(val) - current_log_price) / sigma
                l_bb += w * self.gaussian_kernel(self.z_grid - z, 0.30)
            L_total += self.weights['bb'] * l_bb
            
        med = np.median(L_total)
        mad = np.median(np.abs(L_total - med))
        L_norm = (L_total - med) / (mad if mad > 1e-9 else 1.0)
        return np.clip(L_norm, -6, 6).tolist()

    def get_pool_proximity(self, field_array):
        return field_array[len(field_array) // 2]