from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://gnosis:gnosis_pass@localhost:5432/market_analytics"
    
    # Alpaca
    alpaca_api_key: str = "demo"
    alpaca_secret_key: str = "demo"
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    
    # Massive
    massive_api_key: str = "demo"
    massive_base_url: str = "https://api.massive.io"
    
    # Unusual Whales
    unusual_whales_api_key: str = "demo"
    unusual_whales_base_url: str = "https://api.unusualwhales.com"
    
    # Analytics Configuration
    data_cadence_seconds: int = 60  # 1 minute
    ewma_span: int = 20
    rsi_period: int = 14
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    ichimoku_timeframe_minutes: int = 15
    
    # Collapse Field Configuration
    z_min: float = -4.0
    z_max: float = 4.0
    z_step: float = 0.25
    confidence_levels: list = [0.68, 0.95, 0.997]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
