import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test REST API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "features" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_analytics_not_found(self, client):
        """Test getting analytics for non-existent symbol"""
        response = client.get("/api/v1/analytics/AAPL")
        assert response.status_code == 404
    
    def test_get_bars_empty(self, client):
        """Test getting bars when database is empty"""
        response = client.get("/api/v1/bars/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_indicators_empty(self, client):
        """Test getting indicators when database is empty"""
        response = client.get("/api/v1/indicators/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_collapse_field_empty(self, client):
        """Test getting collapse field when database is empty"""
        response = client.get("/api/v1/collapse-field/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_ingest_endpoint(self, client):
        """Test data ingestion endpoint (will fail without valid API keys)"""
        response = client.post("/api/v1/ingest/AAPL?hours_back=1")
        # Expected to fail with 404 since we don't have valid API credentials
        # In production with valid keys, this would be 200
        assert response.status_code in [404, 500]
    
    def test_compute_endpoint_no_data(self, client):
        """Test compute endpoint with no existing data"""
        response = client.post("/api/v1/compute/AAPL")
        assert response.status_code == 404
