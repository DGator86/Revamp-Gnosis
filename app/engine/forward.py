import numpy as np
from app.config import settings
from app.features.liquidity import LiquidityField

class ForwardMap:
    def __init__(self):
        self.beta_L = settings.forward['beta_L']
        self.max_h = settings.forward['max_horizon']
        self.liq_engine = LiquidityField()

    def compute(self, current_lambda, current_price, current_sigma, l_total_func):
        results = []
        survival = 1.0
        cum_mass = 0.0
        z_grid = self.liq_engine.z_grid
        l_values = np.array(l_total_func)
        h0_dist = np.exp(-0.5 * z_grid**2) / np.sqrt(2*np.pi)
        
        for k in range(1, self.max_h + 1):
            g_k = current_lambda * survival
            survival *= (1 - current_lambda)
            cum_mass += g_k
            
            # Simple interaction approximation
            h_zk = h0_dist * np.exp(self.beta_L * l_values)
            h_zk /= np.sum(h_zk)
            
            results.append({"k": k, "mass": float(g_k), "dist": h_zk.tolist()})
            if cum_mass >= settings.forward['mass_threshold']: break
                
        return {"map": results, "cum_mass": float(cum_mass)}