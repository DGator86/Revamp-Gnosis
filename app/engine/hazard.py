import numpy as np
from app.config import settings

class HazardModel:
    def __init__(self):
        self.intercepts = settings.hazard['intercepts']
        self.coeffs = settings.hazard['coeffs']

    def compute(self, regime, A, pressure_inertia_ratio, squeeze, pool_prox, d_vwap, d_kijun):
        r_idx = 1 if regime == 1 else (2 if regime == -1 else 0)
        logit = (self.intercepts[r_idx] + 
                 self.coeffs['A'] * A + 
                 self.coeffs['P_L'] * pressure_inertia_ratio + 
                 self.coeffs['squeeze'] * (1.0 if squeeze else 0.0) + 
                 self.coeffs['pool'] * pool_prox)
        return 1 / (1 + np.exp(-logit))