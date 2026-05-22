"""Simple tests for Users API."""

import json


def test_get_users_api_returns_json(client):
    """GET /api/users should return JSON."""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_get_user_by_id_returns_correct_data(client, sample_user):
    """GET /api/users/<id> should return user data."""
    response = client.get(f"/api/users/{sample_user.id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == sample_user.id
    assert data["username"] == sample_user.username
