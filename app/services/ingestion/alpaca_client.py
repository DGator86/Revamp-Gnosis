from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.requests import StockBarsRequest, StockQuotesRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from typing import List, Optional
from app.config.settings import settings
from app.models import MarketBar, MarketQuote
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AlpacaIngestion:
    """Handles Alpaca market data ingestion (bars and quotes)"""
    
    def __init__(self):
        self.client = StockHistoricalDataClient(
            api_key=settings.alpaca_api_key,
            secret_key=settings.alpaca_secret_key
        )
        self.stream = None
    
    async def fetch_bars(
        self,
        symbol: str,
        start: datetime,
        end: Optional[datetime] = None,
        timeframe: TimeFrame = TimeFrame.Minute
    ) -> List[dict]:
        """Fetch historical bars from Alpaca"""
        try:
            if end is None:
                end = datetime.utcnow()
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
            
            bars = self.client.get_stock_bars(request)
            
            result = []
            if symbol in bars:
                for bar in bars[symbol]:
                    result.append({
                        'symbol': symbol,
                        'timestamp': bar.timestamp,
                        'open': float(bar.open),
                        'high': float(bar.high),
                        'low': float(bar.low),
                        'close': float(bar.close),
                        'volume': float(bar.volume),
                        'trade_count': bar.trade_count,
                        'vwap': float(bar.vwap) if bar.vwap else None
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching bars from Alpaca: {e}")
            return []
    
    async def fetch_quotes(
        self,
        symbol: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[dict]:
        """Fetch historical quotes from Alpaca"""
        try:
            if end is None:
                end = datetime.utcnow()
            
            request = StockQuotesRequest(
                symbol_or_symbols=symbol,
                start=start,
                end=end
            )
            
            quotes = self.client.get_stock_quotes(request)
            
            result = []
            if symbol in quotes:
                for quote in quotes[symbol]:
                    result.append({
                        'symbol': symbol,
                        'timestamp': quote.timestamp,
                        'bid_price': float(quote.bid_price),
                        'bid_size': float(quote.bid_size),
                        'ask_price': float(quote.ask_price),
                        'ask_size': float(quote.ask_size)
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error fetching quotes from Alpaca: {e}")
            return []
    
    async def store_bars(self, db: Session, bars: List[dict]):
        """Store bars in the database"""
        for bar_data in bars:
            bar = MarketBar(**bar_data)
            db.add(bar)
        db.commit()
    
    async def store_quotes(self, db: Session, quotes: List[dict]):
        """Store quotes in the database"""
        for quote_data in quotes:
            quote = MarketQuote(**quote_data)
            db.add(quote)
        db.commit()
    
    async def start_streaming(self, symbols: List[str], callback):
        """Start real-time streaming (placeholder for WebSocket implementation)"""
        logger.info(f"Starting Alpaca stream for symbols: {symbols}")
        # Actual streaming implementation would use StockDataStream
        pass
