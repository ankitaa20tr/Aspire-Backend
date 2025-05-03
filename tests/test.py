# python3 -m tests.test
# source venvAnkitaTiwari/bin/activate
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "full_name": "Test User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_existing_user():
    # First register
    client.post(
        "/auth/register",
        json={
            "email": "existing@example.com",
            "password": "testpassword",
            "full_name": "Existing User"
        },
    )
    
    # Register again with the same email
    response = client.post(
        "/auth/register",
        json={
            "email": "existing@example.com",
            "password": "anotherpassword",
            "full_name": "Another User"
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login():
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpassword",
            "full_name": "Login User"
        },
    )
    
    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpassword"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    # First register a user
    client.post(
        "/auth/register",
        json={
            "email": "wrongpw@example.com",
            "password": "testpassword",
            "full_name": "Wrong Password User"
        },
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "wrongpw@example.com",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]