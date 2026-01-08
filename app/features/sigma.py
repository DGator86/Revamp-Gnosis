import numpy as np
from app.config import settings

class SigmaCalculator:
    def __init__(self, min_sigma=1e-6):
        self.alpha = 2.0 / (settings.alpha_decay + 1.0)
        self.var_t = 0.0
        self.min_sigma = min_sigma
        self.initialized = False

    def update(self, log_ret):
        if not self.initialized:
            self.var_t = log_ret**2
            self.initialized = True
        else:
            self.var_t = (1 - self.alpha) * self.var_t + self.alpha * (log_ret**2)
        return max(np.sqrt(self.var_t), self.min_sigma)