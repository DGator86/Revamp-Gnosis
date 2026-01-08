from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class MarketBarSchema(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    trade_count: Optional[int] = None
    vwap: Optional[float] = None
    
    class Config:
        from_attributes = True


class TechnicalIndicatorsSchema(BaseModel):
    symbol: str
    timestamp: datetime
    sigma_ewma: Optional[float] = None
    vwap: Optional[float] = None
    rsi: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    tenkan_sen: Optional[float] = None
    kijun_sen: Optional[float] = None
    senkou_span_a: Optional[float] = None
    senkou_span_b: Optional[float] = None
    chikou_span: Optional[float] = None
    
    class Config:
        from_attributes = True


class CollapseFieldSchema(BaseModel):
    symbol: str
    timestamp: datetime
    pool_field_z_values: List[float]
    pool_field_l_values: List[float]
    particle_position: float
    particle_velocity: float
    dealer_prob_p: float
    dealer_prob_q: float
    hazard_lambda: float
    forward_map_tau: List[float]
    forward_map_prob: List[List[float]]
    confidence_levels: List[dict]
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    symbol: str
    timestamp: datetime
    bar: Optional[MarketBarSchema] = None
    indicators: Optional[TechnicalIndicatorsSchema] = None
    collapse_field: Optional[CollapseFieldSchema] = None


class StreamMessage(BaseModel):
    type: str = Field(..., description="Message type: bar, quote, indicator, collapse_field")
    symbol: str
    timestamp: datetime
    data: dict
