import numpy as np
from collections import deque

class Technicals:
    def __init__(self):
        self.vwap_num = 0.0
        self.vwap_denom = 0.0
        self.bb_period = 20
        self.bb_mult = 2.0
        self.bb_prices = deque(maxlen=20)
        self.bb_widths = deque(maxlen=2*390)
        self.rsi_period = 14
        self.gains = deque(maxlen=14)
        self.losses = deque(maxlen=14)
        self.prev_price = None

    def update(self, price, vol):
        self.vwap_num += price * vol
        self.vwap_denom += vol
        vwap = self.vwap_num / self.vwap_denom if self.vwap_denom > 0 else price
        
        self.bb_prices.append(price)
        if len(self.bb_prices) >= self.bb_period:
            mb = np.mean(self.bb_prices)
            sd = np.std(self.bb_prices)
            ub = mb + self.bb_mult * sd
            lb = mb - self.bb_mult * sd
            bbw = (ub - lb) / mb if mb > 0 else 0
        else:
            mb, ub, lb, bbw = price, price, price, 0
            
        self.bb_widths.append(bbw)
        squeeze = False
        if len(self.bb_widths) > 50:
            if bbw <= np.percentile(list(self.bb_widths), 15):
                squeeze = True
                
        rsi_val = 50.0
        if self.prev_price is not None:
            change = price - self.prev_price
            gain = max(change, 0)
            loss = max(-change, 0)
            self.gains.append(gain)
            self.losses.append(loss)
            if len(self.gains) == self.rsi_period:
                avg_gain = np.mean(self.gains)
                avg_loss = np.mean(self.losses)
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    rsi_val = 100.0 - (100.0 / (1.0 + rs))
                elif avg_gain > 0:
                    rsi_val = 100.0
        
        self.prev_price = price
        return {"vwap": vwap, "rsi": (rsi_val-50)/50, "bb": {"mb": mb, "ub": ub, "lb": lb, "width": bbw, "squeeze": squeeze}}

class Ichimoku:
    def __init__(self):
        self.highs_9 = deque(maxlen=9)
        self.lows_9 = deque(maxlen=9)
        self.highs_26 = deque(maxlen=26)
        self.lows_26 = deque(maxlen=26)
        self.highs_52 = deque(maxlen=52)
        self.lows_52 = deque(maxlen=52)
        self.history = deque(maxlen=60)

    def update(self, high, low, close):
        self.highs_9.append(high); self.lows_9.append(low)
        self.highs_26.append(high); self.lows_26.append(low)
        self.highs_52.append(high); self.lows_52.append(low)
        
        tenkan = (max(self.highs_9)+min(self.lows_9))/2 if self.highs_9 else (high+low)/2
        kijun = (max(self.highs_26)+min(self.lows_26))/2 if self.highs_26 else (high+low)/2
        span_a = (tenkan + kijun)/2
        span_b = (max(self.highs_52)+min(self.lows_52))/2 if self.highs_52 else (high+low)/2
        
        self.history.append((span_a, span_b))
        cloud_a, cloud_b = self.history[-26] if len(self.history)>=26 else (span_a, span_b)
        
        state = 1 if close > max(cloud_a, cloud_b) else (-1 if close < min(cloud_a, cloud_b) else 0)
        return {"tenkan": tenkan, "kijun": kijun, "span_a": cloud_a, "span_b": cloud_b, "state": state, "thick": abs(cloud_a-cloud_b)}