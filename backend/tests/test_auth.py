import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_flow(client: AsyncClient):
    """Test user registration flow."""
    response = await client.post(
        "/api/v1/users/signup",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
            "role": "citizen"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

@pytest.mark.asyncio
async def test_login_flow(client: AsyncClient):
    """Test login with valid credentials."""
    # First create a user
    await client.post(
        "/api/v1/users/signup",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
            "full_name": "Login User",
            "role": "citizen"
        }
    )
    
    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid password."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
