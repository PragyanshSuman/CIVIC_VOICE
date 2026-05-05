import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_solution(client: AsyncClient):
    # 1. Setup User & Problem
    await client.post("/api/v1/users/signup", json={"email": "s@test.com", "password": "pass", "full_name": "S User", "role": "citizen"})
    login_res = await client.post("/api/v1/auth/login", data={"username": "s@test.com", "password": "pass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    prob_res = await client.post(
        "/api/v1/problems/",
        json={"title": "Test Prob", "description": "Desc", "category": "General", "latitude": 0, "longitude": 0, "address": "N/A"},
        headers=headers
    )
    problem_id = prob_res.json()["id"]

    # 2. Create Solution
    response = await client.post(
        "/api/v1/solutions/",
        json={
            "title": "Fix it",
            "description": "Just fill it up",
            "problem_id": problem_id
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fix it"
    # Verify AI scoring happened (mocked or real)
    assert "overall_score" in data
