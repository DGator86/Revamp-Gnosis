# Revamp-Gnosis

## Modular Market "Collapse-Field" Analytics Application

A sophisticated market analytics platform that ingests real-time market data at 1-minute cadence and computes advanced technical indicators alongside proprietary "collapse-field" analytics. Built with FastAPI, PostgreSQL, and Docker.

## Features

### Data Ingestion (1-minute cadence)
- **Alpaca Markets**: Real-time bars (OHLCV) and quotes (bid/ask)
- **Massive**: Options Greeks (delta, gamma, theta, vega, rho), Open Interest, Implied Volatility
- **Unusual Whales**: Unusual options flow (sweeps, blocks, splits)

### Technical Indicators
- **Sigma (EWMA)**: Exponentially Weighted Moving Average for volatility estimation
- **VWAP**: Volume Weighted Average Price
- **RSI**: Relative Strength Index (14-period)
- **Bollinger Bands**: 20-period with 2σ standard deviation
- **Ichimoku Cloud**: Optimized for 15-minute timeframe
  - Tenkan-sen (Conversion Line)
  - Kijun-sen (Base Line)
  - Senkou Span A & B (Leading Spans)
  - Chikou Span (Lagging Span)

### Collapse Field Analytics
Advanced probabilistic market analytics:
- **Pool Field L(z)**: Liquidity density distribution over standardized price levels (z ∈ [-4, 4] with 0.25 step)
- **Particle A(t)**: Market state tracking with position and velocity in z-space
- **Dealer Sign (p,q)**: Probabilistic dealer positioning based on order flow
- **Hazard Rate λ(t)**: Instantaneous probability of regime change
- **Forward Map P(τ,z)**: Probability projections with confidence horizons at 1, 5, 15, 30, and 60 minutes

### API
- **REST API**: Full CRUD operations for market data and analytics
- **WebSocket**: Real-time streaming for live market updates
- **OpenAPI/Swagger**: Interactive API documentation at `/docs`

## Architecture

```
revamp-gnosis/
├── app/
│   ├── api/v1/           # REST & WebSocket endpoints
│   ├── config/           # Application settings
│   ├── database/         # Database session & connection
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic schemas
│   └── services/
│       ├── analytics/    # Collapse field computations
│       ├── indicators/   # Technical indicators
│       └── ingestion/    # Market data ingestion
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # API integration tests
├── alembic/             # Database migrations
├── docker-compose.yml   # Container orchestration
├── Dockerfile           # Application container
└── requirements.txt     # Python dependencies
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- API keys for data providers (optional for demo mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DGator86/Revamp-Gnosis.git
   cd Revamp-Gnosis
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

### Development Setup (without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Start PostgreSQL (or use Docker)
   docker run -d --name postgres \
     -e POSTGRES_USER=gnosis \
     -e POSTGRES_PASSWORD=gnosis_pass \
     -e POSTGRES_DB=market_analytics \
     -p 5432:5432 postgres:15-alpine
   
   # Run migrations
   alembic upgrade head
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

### REST Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Ingest Market Data
```bash
# Ingest 24 hours of data for AAPL
curl -X POST "http://localhost:8000/api/v1/ingest/AAPL?hours_back=24"
```

#### Get Analytics
```bash
# Get latest analytics for a symbol
curl http://localhost:8000/api/v1/analytics/AAPL

# Get historical bars
curl http://localhost:8000/api/v1/bars/AAPL?limit=100

# Get technical indicators
curl http://localhost:8000/api/v1/indicators/AAPL?limit=100

# Get collapse field analytics
curl http://localhost:8000/api/v1/collapse-field/AAPL?limit=10
```

#### Compute Analytics
```bash
# Recompute analytics from existing bar data
curl -X POST http://localhost:8000/api/v1/compute/AAPL
```

### WebSocket Streaming

Connect to real-time market data streams:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream/AAPL');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
    // Handle different message types: bar, indicator, collapse_field
};

ws.onopen = () => {
    console.log('Connected to AAPL stream');
};
```

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test suites
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_indicators.py
```

## Database Schema

### Market Data Tables
- `market_bars`: OHLCV bars with timestamps
- `market_quotes`: Real-time bid/ask quotes
- `option_metrics`: Greeks, OI, and IV
- `option_flow`: Unusual options activity

### Analytics Tables
- `technical_indicators`: Computed indicators (EWMA, VWAP, RSI, Bollinger, Ichimoku)
- `collapse_field`: Pool field L(z), particle A(t), dealer probabilities, hazard rates, forward maps

## Configuration

Key settings in `app/config/settings.py`:

```python
# Data cadence
data_cadence_seconds = 60  # 1 minute

# Technical indicators
ewma_span = 20
rsi_period = 14
bollinger_period = 20
ichimoku_timeframe_minutes = 15

# Collapse field
z_min = -4.0
z_max = 4.0
z_step = 0.25
confidence_levels = [0.68, 0.95, 0.997]
```

## Collapse Field Analytics Explained

The collapse field framework models market microstructure as a probabilistic field where price action "collapses" into specific states.

### Pool Field L(z)
Represents liquidity density at standardized price levels. Computed using kernel density estimation on standardized returns.

### Particle A(t)
Models the market state as a particle with:
- **Position**: Current price as z-score relative to recent distribution
- **Velocity**: Rate of change in standardized space

### Dealer Probabilities (p,q)
Estimates the probability of dealer presence:
- **p**: Probability dealer is absorbing selling pressure (buying)
- **q**: Probability dealer is absorbing buying pressure (selling)

### Hazard Rate λ(t)
Instantaneous probability of regime change, influenced by:
- Current volatility
- Volume anomalies (both high and low)

### Forward Map P(τ,z)
Projects probability distribution forward in time with:
- Multiple time horizons (1, 5, 15, 30, 60 minutes)
- Confidence intervals at 68%, 95%, and 99.7% levels
- Combines pool field structure with diffusion dynamics

## API Keys

To use real market data, obtain API keys from:

1. **Alpaca Markets**: https://alpaca.markets/
   - Free paper trading account available
   - Live market data subscriptions

2. **Massive** (placeholder): Configure your options data provider

3. **Unusual Whales**: https://unusualwhales.com/
   - Options flow and unusual activity

Add keys to `.env` file:
```env
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
MASSIVE_API_KEY=your_key_here
UNUSUAL_WHALES_API_KEY=your_key_here
```

## Deployment

### Production Deployment

1. **Use production database**
   ```yaml
   # docker-compose.prod.yml
   services:
     postgres:
       volumes:
         - /data/postgres:/var/lib/postgresql/data
   ```

2. **Enable HTTPS**
   - Use reverse proxy (nginx, traefik)
   - Configure SSL certificates

3. **Scale services**
   ```bash
   docker-compose up -d --scale api=3
   ```

4. **Set up monitoring**
   - Application logs
   - Database performance
   - API metrics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review test examples in `tests/`

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Market data from [Alpaca Markets](https://alpaca.markets/)
- Technical analysis using [TA-Lib](https://github.com/mrjbq7/ta-lib) concepts
- Inspired by advanced market microstructure research