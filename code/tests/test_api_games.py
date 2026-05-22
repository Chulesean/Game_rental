"""Simple tests for Games API."""

import json


def test_get_games_api_returns_json(client, sample_game):
    """GET /api/games should return JSON with games."""
    response = client.get("/api/games")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_get_game_by_id_returns_game_data(client, sample_game):
    """GET /api/games/<id> should return game data."""
    response = client.get(f"/api/games/{sample_game.id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == sample_game.id
    assert data["title"] == sample_game.title
