import aiohttp
from datetime import datetime
from typing import List, Optional
from app.config.settings import settings
from app.models import OptionMetrics
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class MassiveIngestion:
    """Handles Massive options data ingestion (Greeks, OI, IV)"""
    
    def __init__(self):
        self.api_key = settings.massive_api_key
        self.base_url = settings.massive_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def fetch_option_metrics(
        self,
        symbol: str,
        start: datetime,
        end: Optional[datetime] = None
    ) -> List[dict]:
        """Fetch option Greeks, OI, and IV from Massive"""
        try:
            if end is None:
                end = datetime.utcnow()
            
            # Mock implementation - actual API would be called here
            logger.info(f"Fetching option metrics for {symbol} from {start} to {end}")
            
            # In production, this would make actual API calls:
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(
            #         f"{self.base_url}/options/metrics",
            #         headers=self.headers,
            #         params={'symbol': symbol, 'start': start.isoformat(), 'end': end.isoformat()}
            #     ) as response:
            #         data = await response.json()
            #         return self._parse_metrics(data)
            
            # For demo purposes, return empty list
            return []
        
        except Exception as e:
            logger.error(f"Error fetching option metrics from Massive: {e}")
            return []
    
    def _parse_metrics(self, data: dict) -> List[dict]:
        """Parse Massive API response into our format"""
        result = []
        for item in data.get('metrics', []):
            result.append({
                'symbol': item['symbol'],
                'timestamp': datetime.fromisoformat(item['timestamp']),
                'delta': item.get('delta'),
                'gamma': item.get('gamma'),
                'theta': item.get('theta'),
                'vega': item.get('vega'),
                'rho': item.get('rho'),
                'implied_volatility': item.get('iv'),
                'open_interest': item.get('oi'),
                'volume': item.get('volume')
            })
        return result
    
    async def store_metrics(self, db: Session, metrics: List[dict]):
        """Store option metrics in the database"""
        for metric_data in metrics:
            metric = OptionMetrics(**metric_data)
            db.add(metric)
        db.commit()
