import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_problem(client: AsyncClient):
    # 1. Login
    await client.post(
        "/api/v1/users/signup",
        json={"email": "p@test.com", "password": "pass", "full_name": "P User", "role": "citizen"}
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={"username": "p@test.com", "password": "pass"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Problem
    response = await client.post(
        "/api/v1/problems/",
        json={
            "title": "Pothole on Main St",
            "description": "Big pothole damaging cars",
            "category": "Infrastructure",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "address": "123 Main St"
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Pothole on Main St"
    assert data["status"] == "open"

@pytest.mark.asyncio
async def test_get_problems(client: AsyncClient):
    response = await client.get("/api/v1/problems/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
