from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.database import Base


class MarketBar(Base):
    """Stores 1-minute OHLCV bars from Alpaca"""
    __tablename__ = "market_bars"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    trade_count = Column(Integer)
    vwap = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_market_bars_symbol_timestamp', 'symbol', 'timestamp'),
    )


class MarketQuote(Base):
    """Stores real-time quotes from Alpaca"""
    __tablename__ = "market_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    bid_price = Column(Float, nullable=False)
    bid_size = Column(Float, nullable=False)
    ask_price = Column(Float, nullable=False)
    ask_size = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptionMetrics(Base):
    """Stores options Greeks, OI, IV from Massive"""
    __tablename__ = "option_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    rho = Column(Float)
    implied_volatility = Column(Float)
    open_interest = Column(Integer)
    volume = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptionFlow(Base):
    """Stores unusual options flow from Unusual Whales"""
    __tablename__ = "option_flow"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    contract = Column(String(50))
    flow_type = Column(String(20))  # sweep, block, split
    sentiment = Column(String(10))  # bullish, bearish, neutral
    premium = Column(Float)
    size = Column(Integer)
    spot_price = Column(Float)
    strike_price = Column(Float)
    expiry = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TechnicalIndicators(Base):
    """Stores computed technical indicators"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Indicators
    sigma_ewma = Column(Float)
    vwap = Column(Float)
    rsi = Column(Float)
    bollinger_upper = Column(Float)
    bollinger_middle = Column(Float)
    bollinger_lower = Column(Float)
    
    # Ichimoku components (15m timeframe)
    tenkan_sen = Column(Float)
    kijun_sen = Column(Float)
    senkou_span_a = Column(Float)
    senkou_span_b = Column(Float)
    chikou_span = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_technical_indicators_symbol_timestamp', 'symbol', 'timestamp'),
    )


class CollapseField(Base):
    """Stores collapse field analytics (L(z), particle A(t), hazard λ(t))"""
    __tablename__ = "collapse_field"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Pool field L(z) - stored as JSON array for z values
    pool_field_z_values = Column(JSON)  # z values from -4 to 4 step 0.25
    pool_field_l_values = Column(JSON)  # L(z) values
    
    # Particle tracking
    particle_position = Column(Float)
    particle_velocity = Column(Float)
    
    # Probabilistic dealer sign
    dealer_prob_p = Column(Float)  # probability parameter p
    dealer_prob_q = Column(Float)  # probability parameter q
    
    # Hazard rate
    hazard_lambda = Column(Float)
    
    # Forward map P(τ,z) with confidence
    forward_map_tau = Column(JSON)  # array of time horizons
    forward_map_prob = Column(JSON)  # probability distributions
    confidence_levels = Column(JSON)  # confidence intervals
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_collapse_field_symbol_timestamp', 'symbol', 'timestamp'),
    )
