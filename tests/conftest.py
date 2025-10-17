# Test Configuration and Utilities

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, QRCode, QRScan
from app.utils.auth import create_access_token
import tempfile
import os


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        is_active=True,
        is_verified=True,
        tier="free"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_qr_code(db_session, test_user):
    """Create a test QR code."""
    qr_code = QRCode(
        user_id=test_user.id,
        short_url="test123",
        destination_url="https://example.com",
        title="Test QR Code",
        description="Test description"
    )
    db_session.add(qr_code)
    db_session.commit()
    db_session.refresh(qr_code)
    return qr_code


@pytest.fixture
def temp_file():
    """Create a temporary file for testing file uploads."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(b"fake image data")
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_user(email="test@example.com", tier="free"):
        return User(
            email=email,
            password_hash="hashed_password",
            is_active=True,
            is_verified=True,
            tier=tier
        )
    
    @staticmethod
    def create_qr_code(user_id, destination_url="https://example.com"):
        return QRCode(
            user_id=user_id,
            short_url="test123",
            destination_url=destination_url,
            title="Test QR Code",
            description="Test description"
        )
    
    @staticmethod
    def create_qr_scan(user_id=None, content="https://example.com"):
        return QRScan(
            user_id=user_id,
            content=content,
            filename="test.png",
            file_size=1024
        )


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory()


# Test utilities
def assert_response_success(response, expected_status=200):
    """Assert that response is successful."""
    assert response.status_code == expected_status


def assert_response_error(response, expected_status=400):
    """Assert that response is an error."""
    assert response.status_code == expected_status
    assert "error" in response.json()


def assert_qr_code_response(response_data, expected_fields=None):
    """Assert QR code response has expected fields."""
    if expected_fields is None:
        expected_fields = ["id", "short_url", "destination_url", "title"]
    
    for field in expected_fields:
        assert field in response_data


def assert_user_response(response_data, expected_fields=None):
    """Assert user response has expected fields."""
    if expected_fields is None:
        expected_fields = ["id", "email", "is_active", "tier"]
    
    for field in expected_fields:
        assert field in response_data


# Performance testing utilities
def measure_time(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    return wrapper


# Mock utilities
class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value, ex=None):
        self.data[key] = value
        return True
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    def exists(self, key):
        return key in self.data


@pytest.fixture
def mock_redis():
    """Provide mock Redis client."""
    return MockRedis()
