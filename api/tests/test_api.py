"""
Unit tests for the API.
We MOCK Redis — meaning we pretend Redis exists without actually running it.
This lets tests run anywhere without a real Redis server.
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Import our app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from main import app

# TestClient lets us make fake HTTP requests to our API in tests
client = TestClient(app)


@pytest.fixture
def mock_redis():
    """
    This fixture creates a fake Redis object.
    Every test that uses 'mock_redis' gets a fresh fake Redis.
    """
    with patch('main.get_redis') as mock_get_redis:
        mock_r = MagicMock()
        mock_get_redis.return_value = mock_r
        yield mock_r


def test_health_check_success(mock_redis):
    """Test 1: Health endpoint returns healthy when Redis is reachable"""
    mock_redis.ping.return_value = True  # Fake Redis responds to ping
    
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"


def test_create_job_success(mock_redis):
    """Test 2: Creating a job stores it in Redis and returns a job ID"""
    mock_redis.set.return_value = True
    mock_redis.lpush.return_value = 1
    
    response = client.post("/jobs", json={"payload": "test-job-data"})
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    
    # Verify Redis was called correctly
    assert mock_redis.set.called
    assert mock_redis.lpush.called


def test_get_job_not_found(mock_redis):
    """Test 3: Getting a non-existent job returns 404"""
    mock_redis.get.return_value = None  # Redis returns nothing
    
    response = client.get("/jobs/fake-job-id-that-doesnt-exist")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_get_job_success(mock_redis):
    """Test 4: Getting an existing job returns its data"""
    job_data = {
        "id": "abc-123",
        "payload": "some work",
        "status": "completed"
    }
    # Fake Redis returns this job when asked
    mock_redis.get.return_value = json.dumps(job_data)
    
    response = client.get("/jobs/abc-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "abc-123"
    assert data["status"] == "completed"


def test_create_job_missing_payload():
    """Test 5: Creating a job without payload returns 422 validation error"""
    response = client.post("/jobs", json={})  # Missing 'payload' field
    
    assert response.status_code == 422  # Unprocessable Entity


def test_health_check_redis_down(mock_redis):
    """Test 6: Health endpoint returns 503 when Redis is unreachable"""
    mock_redis.ping.side_effect = Exception("Connection refused")
    
    response = client.get("/health")
    
    assert response.status_code == 503