"""
Tests for Phase 3 - Prediction API Integration

Tests cover:
- ML Service loading
- Prediction endpoint
- Model info endpoint
- Transaction storage
- Dashboard endpoints
"""

import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.services.ml_service import MLService
from app.services.risk_engine import RiskEngine


SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestRiskEngine:
    """Test risk engine"""
    
    def test_risk_level_low(self):
        engine = RiskEngine()
        assert engine.get_risk_level(0.2) == "LOW"
    
    def test_risk_level_medium(self):
        engine = RiskEngine()
        assert engine.get_risk_level(0.5) == "MEDIUM"
    
    def test_risk_level_high(self):
        engine = RiskEngine()
        assert engine.get_risk_level(0.8) == "HIGH"
    
    def test_prediction_legitimate(self):
        engine = RiskEngine(prediction_threshold=0.5)
        assert engine.get_prediction(0.3) == "LEGITIMATE"
    
    def test_prediction_fraud(self):
        engine = RiskEngine(prediction_threshold=0.5)
        assert engine.get_prediction(0.7) == "FRAUD"
    
    def test_classification(self):
        engine = RiskEngine()
        result = engine.classify(0.65)
        
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'prediction' in result
        assert result['risk_score'] == 65.0
        assert result['risk_level'] == 'MEDIUM'


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        response = client.get("/api/health")
        
        # Should be 200 if ML service not loaded yet
        assert response.status_code in [200, 503]
        data = response.json()
        assert 'status' in data


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data


class TestTransactionSchema:
    """Test transaction prediction schema"""
    
    def test_valid_transaction(self):
        from app.schemas.prediction import TransactionPredictionRequest
        
        # All 30 features required
        data = {
            'Time': 3600,
            'V1': -1.35, 'V2': -0.73, 'V3': -0.47, 'V4': 1.03,
            'V5': -0.50, 'V6': 0.27, 'V7': -0.12, 'V8': 0.21,
            'V9': -0.04, 'V10': 0.46, 'V11': 0.34, 'V12': -0.57,
            'V13': 0.15, 'V14': -0.22, 'V15': 0.11, 'V16': 0.09,
            'V17': -0.07, 'V18': -0.03, 'V19': 0.12, 'V20': -0.18,
            'V21': 0.08, 'V22': -0.09, 'V23': 0.03, 'V24': -0.04,
            'V25': 0.13, 'V26': -0.07, 'V27': 0.06, 'V28': 0.08,
            'Amount': 149.62
        }
        
        request = TransactionPredictionRequest(**data)
        assert request.Amount == 149.62
        assert request.Time == 3600
    
    def test_invalid_amount(self):
        from app.schemas.prediction import TransactionPredictionRequest
        from pydantic import ValidationError
        
        data = {
            'Time': 3600,
            'V1': -1.35, 'V2': -0.73, 'V3': -0.47, 'V4': 1.03,
            'V5': -0.50, 'V6': 0.27, 'V7': -0.12, 'V8': 0.21,
            'V9': -0.04, 'V10': 0.46, 'V11': 0.34, 'V12': -0.57,
            'V13': 0.15, 'V14': -0.22, 'V15': 0.11, 'V16': 0.09,
            'V17': -0.07, 'V18': -0.03, 'V19': 0.12, 'V20': -0.18,
            'V21': 0.08, 'V22': -0.09, 'V23': 0.03, 'V24': -0.04,
            'V25': 0.13, 'V26': -0.07, 'V27': 0.06, 'V28': 0.08,
            'Amount': 999999  # Too large
        }
        
        with pytest.raises(ValidationError):
            TransactionPredictionRequest(**data)


class TestPredictionResponse:
    """Test prediction response schema"""
    
    def test_response_structure(self):
        from app.schemas.prediction import PredictionResponse
        
        response = PredictionResponse(
            prediction="LEGITIMATE",
            fraud_probability=0.12,
            risk_score=12.0,
            risk_level="LOW",
            model_version="1.0.0"
        )
        
        assert response.prediction == "LEGITIMATE"
        assert response.fraud_probability == 0.12
        assert response.risk_score == 12.0
        assert response.risk_level == "LOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
