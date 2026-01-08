from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
import numpy as np

from app.database import get_db
from app.models import MarketBar, TechnicalIndicators, CollapseField
from app.schemas import (
    MarketBarSchema,
    TechnicalIndicatorsSchema,
    CollapseFieldSchema,
    AnalyticsResponse,
)
from app.services.ingestion import AlpacaIngestion, MassiveIngestion, UnusualWhalesIngestion
from app.services.indicators import TechnicalIndicatorService
from app.services.analytics import CollapseFieldAnalytics

router = APIRouter(prefix="/api/v1", tags=["analytics"])

# Initialize services
alpaca_client = AlpacaIngestion()
massive_client = MassiveIngestion()
whales_client = UnusualWhalesIngestion()
indicator_service = TechnicalIndicatorService()
collapse_analytics = CollapseFieldAnalytics()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/analytics/{symbol}", response_model=AnalyticsResponse)
async def get_analytics(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get latest analytics for a symbol"""
    
    # Get latest bar
    latest_bar = db.query(MarketBar).filter(
        MarketBar.symbol == symbol
    ).order_by(desc(MarketBar.timestamp)).first()
    
    # Get latest indicators
    latest_indicators = db.query(TechnicalIndicators).filter(
        TechnicalIndicators.symbol == symbol
    ).order_by(desc(TechnicalIndicators.timestamp)).first()
    
    # Get latest collapse field
    latest_collapse = db.query(CollapseField).filter(
        CollapseField.symbol == symbol
    ).order_by(desc(CollapseField.timestamp)).first()
    
    if not latest_bar:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
    
    return AnalyticsResponse(
        symbol=symbol,
        timestamp=latest_bar.timestamp,
        bar=MarketBarSchema.from_orm(latest_bar) if latest_bar else None,
        indicators=TechnicalIndicatorsSchema.from_orm(latest_indicators) if latest_indicators else None,
        collapse_field=CollapseFieldSchema.from_orm(latest_collapse) if latest_collapse else None,
    )


@router.get("/bars/{symbol}", response_model=List[MarketBarSchema])
async def get_bars(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get historical bars for a symbol"""
    bars = db.query(MarketBar).filter(
        MarketBar.symbol == symbol
    ).order_by(desc(MarketBar.timestamp)).limit(limit).all()
    
    return [MarketBarSchema.from_orm(bar) for bar in bars]


@router.get("/indicators/{symbol}", response_model=List[TechnicalIndicatorsSchema])
async def get_indicators(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get historical technical indicators for a symbol"""
    indicators = db.query(TechnicalIndicators).filter(
        TechnicalIndicators.symbol == symbol
    ).order_by(desc(TechnicalIndicators.timestamp)).limit(limit).all()
    
    return [TechnicalIndicatorsSchema.from_orm(ind) for ind in indicators]


@router.get("/collapse-field/{symbol}", response_model=List[CollapseFieldSchema])
async def get_collapse_field(
    symbol: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get historical collapse field analytics for a symbol"""
    fields = db.query(CollapseField).filter(
        CollapseField.symbol == symbol
    ).order_by(desc(CollapseField.timestamp)).limit(limit).all()
    
    return [CollapseFieldSchema.from_orm(field) for field in fields]


@router.post("/ingest/{symbol}")
async def ingest_data(
    symbol: str,
    hours_back: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db)
):
    """
    Ingest data for a symbol and compute analytics
    
    This endpoint:
    1. Fetches bars from Alpaca
    2. Computes technical indicators
    3. Computes collapse field analytics
    4. Stores everything in the database
    """
    start_time = datetime.utcnow() - timedelta(hours=hours_back)
    end_time = datetime.utcnow()
    
    # Fetch bars from Alpaca
    bars_data = await alpaca_client.fetch_bars(symbol, start_time, end_time)
    
    if not bars_data:
        raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
    
    # Store bars
    await alpaca_client.store_bars(db, bars_data)
    
    # Compute indicators
    df = pd.DataFrame(bars_data)
    df_with_indicators = indicator_service.compute_all_indicators(df)
    
    # Store indicators
    for idx, row in df_with_indicators.iterrows():
        indicator = TechnicalIndicators(
            symbol=symbol,
            timestamp=row['timestamp'],
            sigma_ewma=row.get('sigma_ewma'),
            vwap=row.get('vwap'),
            rsi=row.get('rsi'),
            bollinger_upper=row.get('bollinger_upper'),
            bollinger_middle=row.get('bollinger_middle'),
            bollinger_lower=row.get('bollinger_lower'),
            tenkan_sen=row.get('tenkan_sen'),
            kijun_sen=row.get('kijun_sen'),
            senkou_span_a=row.get('senkou_span_a'),
            senkou_span_b=row.get('senkou_span_b'),
            chikou_span=row.get('chikou_span'),
        )
        db.add(indicator)
    
    # Compute collapse field analytics
    prices = df['close'].values
    volumes = df['volume'].values
    timestamps = df['timestamp'].apply(lambda x: x.timestamp()).values
    
    collapse_data = collapse_analytics.compute_full_analytics(
        prices, volumes, timestamps
    )
    
    # Store collapse field
    collapse_field = CollapseField(
        symbol=symbol,
        timestamp=df_with_indicators.iloc[-1]['timestamp'],
        **collapse_data
    )
    db.add(collapse_field)
    
    db.commit()
    
    return {
        "status": "success",
        "symbol": symbol,
        "bars_ingested": len(bars_data),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/compute/{symbol}")
async def compute_analytics(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Compute analytics from existing bar data
    
    Useful for recomputing indicators and collapse field 
    without re-ingesting data
    """
    # Get recent bars
    bars = db.query(MarketBar).filter(
        MarketBar.symbol == symbol
    ).order_by(MarketBar.timestamp).limit(1000).all()
    
    if not bars:
        raise HTTPException(status_code=404, detail=f"No bars found for {symbol}")
    
    # Convert to DataFrame
    bars_data = [{
        'timestamp': bar.timestamp,
        'open': bar.open,
        'high': bar.high,
        'low': bar.low,
        'close': bar.close,
        'volume': bar.volume,
    } for bar in bars]
    
    df = pd.DataFrame(bars_data)
    
    # Compute indicators
    df_with_indicators = indicator_service.compute_all_indicators(df)
    
    # Store indicators (only new ones)
    latest_indicator_time = db.query(TechnicalIndicators.timestamp).filter(
        TechnicalIndicators.symbol == symbol
    ).order_by(desc(TechnicalIndicators.timestamp)).first()
    
    for idx, row in df_with_indicators.iterrows():
        if latest_indicator_time is None or row['timestamp'] > latest_indicator_time[0]:
            indicator = TechnicalIndicators(
                symbol=symbol,
                timestamp=row['timestamp'],
                sigma_ewma=row.get('sigma_ewma'),
                vwap=row.get('vwap'),
                rsi=row.get('rsi'),
                bollinger_upper=row.get('bollinger_upper'),
                bollinger_middle=row.get('bollinger_middle'),
                bollinger_lower=row.get('bollinger_lower'),
                tenkan_sen=row.get('tenkan_sen'),
                kijun_sen=row.get('kijun_sen'),
                senkou_span_a=row.get('senkou_span_a'),
                senkou_span_b=row.get('senkou_span_b'),
                chikou_span=row.get('chikou_span'),
            )
            db.add(indicator)
    
    # Compute collapse field
    prices = df['close'].values
    volumes = df['volume'].values
    timestamps = df['timestamp'].apply(lambda x: x.timestamp()).values
    
    collapse_data = collapse_analytics.compute_full_analytics(
        prices, volumes, timestamps
    )
    
    collapse_field = CollapseField(
        symbol=symbol,
        timestamp=df_with_indicators.iloc[-1]['timestamp'],
        **collapse_data
    )
    db.add(collapse_field)
    
    db.commit()
    
    return {
        "status": "success",
        "symbol": symbol,
        "bars_processed": len(bars),
        "timestamp": datetime.utcnow().isoformat()
    }
