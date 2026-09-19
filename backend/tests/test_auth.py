"""
Tests for FraudGuard AI Backend - Phase 1

Tests cover:
- Database connectivity
- Authentication endpoints
- Health check
- User registration and login
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, verify_password
from app.models.models import User


# Test database configuration
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create test client with overridden database"""
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


class TestHealth:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "model" in data
    
    def test_readiness_check(self, client):
        """Test readiness check"""
        response = client.get("/api/ready")
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # Register first user
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "securepassword123"
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test2@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/api/auth/register",
            json={
                "username": "user1",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/auth/register",
            json={
                "username": "user2",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == "testuser"
    
    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        # Register user
        client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "correctpassword123"
            }
        )
        
        # Try login with wrong password
        response = client.post(
            "/api/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword123"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client):
        """Test getting current user info"""
        # Register and login
        register_response = client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "securepassword123"
            }
        )
        token = register_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        # FastAPI will return 403 for missing auth
        assert response.status_code in [401, 403]


class TestSecurity:
    """Test security utilities"""
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = "securepassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_password_hashing_consistency(self):
        """Test that same password gets different hashes (bcrypt salt)"""
        password = "securepassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestRoot:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root API endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
