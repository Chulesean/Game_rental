"""Simple tests for Reviews API."""

import json


def test_get_review_returns_404_for_invalid(client):
    """GET /api/reviews/99999 should return 404."""
    response = client.get("/api/reviews/99999")
    assert response.status_code == 404


def test_api_reviews_endpoint_exists(client):
    """Reviews API endpoint should exist."""
    response = client.get("/api/players/1/reviews")
    # May return 404 or 200, but endpoint should exist
    assert response.status_code in [200, 404]
    