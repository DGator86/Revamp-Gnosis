from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import analytics, websocket
from app.database import Base, engine
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Revamp-Gnosis Market Analytics",
    description="Modular market collapse-field analytics with 1m cadence data ingestion",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Revamp-Gnosis Market Analytics API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "features": [
            "1-minute market data ingestion (Alpaca)",
            "Options Greeks/OI/IV (Massive)",
            "Unusual options flow (Unusual Whales)",
            "Technical indicators (EWMA, VWAP, RSI, Bollinger, Ichimoku)",
            "Collapse field analytics (L(z), particle A(t), dealer sign, hazard λ(t), forward map P(τ,z))",
            "REST API endpoints",
            "WebSocket streaming"
        ]
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting Revamp-Gnosis Market Analytics API")
    logger.info("Database tables created/verified")
    logger.info("API ready to accept connections")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down Revamp-Gnosis Market Analytics API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
