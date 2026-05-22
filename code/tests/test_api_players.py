"""Simple tests for Players API."""

import json


def test_get_players_api_returns_json(client):
    """GET /api/players should return JSON."""
    response = client.get("/api/players")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_get_player_by_id_returns_404_for_invalid(client):
    """GET /api/players/99999 should return 404."""
    response = client.get("/api/players/99999")
    assert response.status_code == 404
    