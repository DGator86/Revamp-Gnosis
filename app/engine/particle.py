import numpy as np
from app.config import settings

class ParticleMapper:
    def __init__(self):
        self.s = 0.0
        self.epsilon = float(settings.particle['epsilon'])
        
    def update(self, spread, ask, bid, microvol, quote_size, ofi_z, dealer_z, flow_impulse_z, shock_val):
        s0 = 0.5 * np.log(ask/bid)
        denom = self.epsilon + spread + microvol - quote_size
        inertia = 1.0 / (denom if denom > 1e-6 else 1e-6)
        
        pressure = (1.0 * ofi_z + 0.7 * dealer_z + 0.5 * flow_impulse_z + settings.particle['shock_weight'] * shock_val)
        cons = 0.20 * abs(pressure) / inertia
        self.s = max(0, s0 - cons)
        
        return {"s": self.s, "pressure": pressure, "inertia": inertia, "annihilation": 1.0 - self.s / (s0 + 1e-6)}