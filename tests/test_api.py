"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import AsyncMock

# Add backend to path so we can import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from main import app
from config import settings

def test_health_endpoint(monkeypatch):
    with TestClient(app) as live_client:
        mock_check = AsyncMock(return_value=True)
        monkeypatch.setattr(live_client.app.state.llm_service, "check_connection", mock_check)
        
        response = live_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "model" in data
        assert "version" in data
        assert data["llm_connected"] is True

def test_locations_endpoint():
    with TestClient(app) as live_client:
        response = live_client.get("/api/locations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Koramangala" in data

def test_cuisines_endpoint():
    with TestClient(app) as live_client:
        response = live_client.get("/api/cuisines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

def test_validation_errors():
    with TestClient(app) as live_client:
        # Invalid budget (must be low, medium, high)
        payload = {
            "location": "Koramangala",
            "budget": "super_cheap",
            "cuisines": ["Italian"]
        }
        response = live_client.post("/api/recommend", json=payload)
        assert response.status_code == 422
        
        # Missing location
        payload = {
            "budget": "low",
            "cuisines": ["Italian"]
        }
        response = live_client.post("/api/recommend", json=payload)
        assert response.status_code == 422
        
        # Invalid rating
        payload = {
            "location": "Koramangala",
            "budget": "low",
            "min_rating": 10.0
        }
        response = live_client.post("/api/recommend", json=payload)
        assert response.status_code == 422

def test_recommend_endpoint_success(monkeypatch):
    from models.schemas import Recommendation
    mock_recs = [
        Recommendation(
            rank=1,
            restaurant_name="Test Rest",
            cuisines="Italian",
            location="Koramangala",
            aggregate_rating=4.5,
            average_cost_for_two=600,
            explanation="Good mock"
        )
    ]
    
    with TestClient(app) as live_client:
        mock_get_recs = AsyncMock(return_value=mock_recs)
        monkeypatch.setattr(live_client.app.state.llm_service, "get_recommendations", mock_get_recs)
        
        payload = {
            "location": "Koramangala",
            "budget": "medium",
            "cuisines": ["Italian"],
            "min_rating": 4.0
        }
        response = live_client.post("/api/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) == 1
        assert data["recommendations"][0]["restaurant_name"] == "Test Rest"
        assert "summary" in data
        assert "total_candidates_filtered" in data

def test_recommend_endpoint_fallback(monkeypatch):
    with TestClient(app) as live_client:
        mock_get_recs_fail = AsyncMock(return_value=[])
        monkeypatch.setattr(live_client.app.state.llm_service, "get_recommendations", mock_get_recs_fail)
        
        payload = {
            "location": "Koramangala",
            "budget": "medium",
            "cuisines": ["Italian"]
        }
        response = live_client.post("/api/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Should return fallback recommendations from the dataset
        assert len(data["recommendations"]) > 0
        assert "high load" in data["summary"].lower()
