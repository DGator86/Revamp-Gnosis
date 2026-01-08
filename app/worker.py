import asyncio
import json
import numpy as np
from app.config import settings, symbol_config
from app.ingest.providers import DataProvider
from app.features.sigma import SigmaCalculator
from app.features.technicals import Technicals, Ichimoku
from app.features.liquidity import LiquidityField
from app.engine.particle import ParticleMapper
from app.engine.dealer import DealerFilter
from app.engine.hazard import HazardModel
from app.engine.forward import ForwardMap
from app.storage.db import engine
from app.storage.models import MarketState
from sqlmodel import Session

class SymbolProcessor:
    def __init__(self, symbol):
        self.symbol = symbol
        self.sigma = SigmaCalculator()
        self.tech = Technicals()
        self.ichi = Ichimoku()
        self.liq = LiquidityField()
        self.part = ParticleMapper()
        self.dealer = DealerFilter()
        self.haz = HazardModel()
        self.fwd = ForwardMap()
        self.last_log = None

    async def process(self, provider):
        bar = await provider.get_latest_bar(self.symbol)
        if not bar: return None
        price = bar['close']
        log_p = np.log(price)
        ret = log_p - self.last_log if self.last_log else 0.0
        self.last_log = log_p
        
        curr_sig = self.sigma.update(ret)
        t_res = self.tech.update(price, bar['volume'])
        i_res = self.ichi.update(bar['high'], bar['low'], price)
        
        comps = {'vwap': {'price': t_res['vwap']}, 'bb': t_res['bb']}
        l_field = self.liq.compute_field(log_p, curr_sig, comps)
        
        quotes = await provider.get_quotes(self.symbol)
        part_res = self.part.update(0.01, quotes['ask_price'], quotes['bid_price'], 0, 0, 0, 0, 0, 0)
        
        lam = self.haz.compute(i_res['state'], part_res['annihilation'], 0, False, 0, 0, 0)
        fwd = self.fwd.compute(lam, price, curr_sig, l_field)
        
        return MarketState(timestamp=bar['timestamp'], symbol=self.symbol, price=price, log_price=log_p,
                           returns=ret, sigma=curr_sig, vwap=t_res['vwap'], rsi=t_res['rsi'],
                           bb_upper=t_res['bb']['ub'], bb_lower=t_res['bb']['lb'], bb_width=t_res['bb']['width'],
                           ichi_cloud_state=i_res['state'], ichi_cloud_thick=i_res['thick'],
                           spread=0.01, pressure=part_res['pressure'], inertia=part_res['inertia'],
                           annihilation=part_res['annihilation'], dealer_p=0.5, dealer_q=0.5, dealer_feedback=0,
                           lambda_t=lam, pool_field=l_field, forward_map=fwd)

async def run_worker_loop(manager):
    provider = DataProvider()
    processors = {s: SymbolProcessor(s) for s in symbol_config.symbols}
    while True:
        async with Session(engine) as session:
            for sym, proc in processors.items():
                state = await proc.process(provider)
                if state:
                    session.add(state)
                    await session.commit()
                    msg = json.dumps({"symbol": sym, "price": state.price, "sigma": state.sigma, "lambda": state.lambda_t, "map": state.forward_map}, default=str)
                    await manager.broadcast(msg)
        await asyncio.sleep(5)