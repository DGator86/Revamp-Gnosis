from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, ARRAY, Float, JSON, Column

class MarketState(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(index=True)
    symbol: str = Field(index=True)
    price: float
    log_price: float
    returns: float
    sigma: float
    vwap: float
    rsi: float
    bb_upper: float
    bb_lower: float
    bb_width: float
    ichi_cloud_state: int
    ichi_cloud_thick: float
    spread: float
    pressure: float
    inertia: float
    annihilation: float
    dealer_p: float
    dealer_q: float
    dealer_feedback: float
    lambda_t: float
    pool_field: List[float] = Field(sa_column=Column(ARRAY(Float)))
    forward_map: Optional[dict] = Field(default=None, sa_column=Column(JSON))

class OptionSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    timestamp: datetime
    data: dict = Field(sa_column=Column(JSON))