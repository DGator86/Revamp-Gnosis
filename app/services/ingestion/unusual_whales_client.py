import aiohttp
from datetime import datetime
from typing import List, Optional
from app.config.settings import settings
from app.models import OptionFlow
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class UnusualWhalesIngestion:
    """Handles Unusual Whales options flow data ingestion"""
    
    def __init__(self):
        self.api_key = settings.unusual_whales_api_key
        self.base_url = settings.unusual_whales_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def fetch_option_flow(
        self,
        symbol: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[dict]:
        """Fetch unusual options flow from Unusual Whales"""
        try:
            if end is None:
                end = datetime.utcnow()
            
            # Mock implementation - actual API would be called here
            logger.info(f"Fetching option flow for {symbol} from {start} to {end}")
            
            # In production, this would make actual API calls:
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(
            #         f"{self.base_url}/flow",
            #         headers=self.headers,
            #         params={'symbol': symbol, 'start': start.isoformat(), 'end': end.isoformat()}
            #     ) as response:
            #         data = await response.json()
            #         return self._parse_flow(data)
            
            # For demo purposes, return empty list
            return []
        
        except Exception as e:
            logger.error(f"Error fetching option flow from Unusual Whales: {e}")
            return []
    
    def _parse_flow(self, data: dict) -> List[dict]:
        """Parse Unusual Whales API response into our format"""
        result = []
        for item in data.get('flows', []):
            result.append({
                'symbol': item['symbol'],
                'timestamp': datetime.fromisoformat(item['timestamp']),
                'contract': item.get('contract'),
                'flow_type': item.get('type'),  # sweep, block, split
                'sentiment': item.get('sentiment'),  # bullish, bearish, neutral
                'premium': item.get('premium'),
                'size': item.get('size'),
                'spot_price': item.get('spot_price'),
                'strike_price': item.get('strike'),
                'expiry': datetime.fromisoformat(item['expiry']) if item.get('expiry') else None
            })
        return result
    
    async def store_flow(self, db: Session, flows: List[dict]):
        """Store option flow in the database"""
        for flow_data in flows:
            flow = OptionFlow(**flow_data)
            db.add(flow)
        db.commit()
