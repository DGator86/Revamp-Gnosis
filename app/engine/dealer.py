import numpy as np
from app.config import settings

class DealerFilter:
    def __init__(self):
        self.p = 0.5; self.q = 0.5
        self.stay_prob = settings.dealer['stay_prob']
        self.flip_prob = settings.dealer['flip_prob']

    def update(self, z_features, gex_abs_norm, is_stale=False):
        E_t = np.sum(z_features) 
        p_prior = self.p * self.stay_prob + (1 - self.p) * self.flip_prob
        
        logit_post = np.log(p_prior / (1 - p_prior + 1e-9)) - E_t
        self.p = 1 / (1 + np.exp(-logit_post))
        
        self.q = 1 / (1 + np.exp(-(1.0 + 2.0*abs(2*self.p - 1))))
        feedback = (2 * self.p - 1) * gex_abs_norm * self.q
        if is_stale: feedback *= 0.3
        return {"p": self.p, "q": self.q, "feedback": feedback}