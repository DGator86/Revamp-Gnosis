import numpy as np
from datetime import datetime
import random

class DataProvider:
    def __init__(self):
        self.price = 400.0
    
    async def get_latest_bar(self, symbol):
        self.price *= np.exp(np.random.normal(0, 0.001))
        return {
            "timestamp": datetime.now(),
            "close": self.price,
            "high": self.price * 1.001,
            "low": self.price * 0.999,
            "volume": 1000
        }

    async def get_quotes(self, symbol):
        return {"bid_price": self.price-0.01, "ask_price": self.price+0.01, "bid_size": 10, "ask_size": 10}

    async def get_options_chain(self, symbol):
        return {"strikes": [], "gex_abs": 500.0}

    async def get_flow(self, symbol):
        return {"ofi": 0, "flow_impulse": 0, "sweep_rate": 0, "shock": 0}