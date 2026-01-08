# Contributing to Revamp-Gnosis

Thank you for your interest in contributing to Revamp-Gnosis! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, Docker version)
- **Logs or error messages** if applicable
- **Code samples** demonstrating the issue

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case** for the enhancement
- **Detailed description** of the proposed functionality
- **Examples** of how it would work
- **Potential implementation approach** (optional)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Ensure all tests pass** (`make test`)
5. **Run linters** (`make lint`)
6. **Update documentation** as needed
7. **Commit with clear messages** following conventional commits
8. **Push to your fork** and submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+ (if running locally without Docker)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Revamp-Gnosis.git
cd Revamp-Gnosis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# Run the application
uvicorn app.main:app --reload
```

## Coding Standards

### Python Style Guide

- Follow **PEP 8** style guide
- Use **Black** for code formatting (line length: 100)
- Use **isort** for import sorting
- Use **type hints** for all functions
- Maintain **test coverage** above 80%

### Code Formatting

```bash
# Format code
make format

# Check formatting
make lint

# Type checking
make typecheck
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(analytics): add dealer positioning probability calculation

fix(ingestion): handle alpaca rate limiting errors

docs(readme): update API examples with WebSocket usage
```

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

```python
def test_collapse_field_computes_pool_field_correctly():
    # Arrange
    bars = create_test_bars()

    # Act
    result = compute_pool_field(bars)

    # Assert
    assert len(result.z_levels) == 33
    assert result.liquidity_density.sum() > 0
```

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Update API documentation in `docs/` directory

```python
def compute_hazard_rate(
    volatility: float,
    volume_anomaly: float,
    threshold: float = 2.0
) -> float:
    """
    Compute instantaneous probability of regime change.

    Args:
        volatility: Current market volatility (sigma)
        volume_anomaly: Volume z-score
        threshold: Anomaly threshold for hazard trigger

    Returns:
        Hazard rate lambda(t) in [0, 1]

    Raises:
        ValueError: If volatility is negative
    """
    pass
```

## Project Structure

```
revamp-gnosis/
├── app/
│   ├── api/v1/           # API endpoints
│   ├── config/           # Configuration
│   ├── database/         # Database setup
│   ├── models/           # ORM models
│   ├── schemas/          # Pydantic schemas
│   └── services/         # Business logic
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Shared fixtures
├── docs/                 # Documentation
├── alembic/              # Database migrations
└── .github/              # CI/CD workflows
```

## Adding New Features

### Analytics Features

1. Add computation logic in `app/services/analytics/`
2. Create database models in `app/models/`
3. Add Pydantic schemas in `app/schemas/`
4. Create API endpoints in `app/api/v1/`
5. Add tests in `tests/unit/` and `tests/integration/`
6. Update documentation

### Data Ingestion

1. Create client in `app/services/ingestion/`
2. Add API configuration to settings
3. Update database models if needed
4. Add ingestion endpoints
5. Create tests with mocked API responses

## Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/unit/test_collapse_field.py

# With coverage
make test-coverage

# Integration tests only
pytest tests/integration/
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Release Process

1. Update version in `app/main.py`
2. Update `CHANGELOG.md`
3. Create release PR
4. Merge to main after approval
5. Tag release: `git tag -a v1.x.x -m "Release v1.x.x"`
6. Push tag: `git push origin v1.x.x`
7. GitHub Actions will build and publish

## Getting Help

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Review `/docs` and API docs at `/docs` endpoint

## Recognition

Contributors will be recognized in:
- `CHANGELOG.md` for each release
- GitHub contributors page
- Project documentation

Thank you for contributing to Revamp-Gnosis!
