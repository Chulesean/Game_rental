"""Simple tests for Bookings API."""

import json


def test_get_bookings_requires_login(client):
    """GET /api/bookings should require authentication."""
    response = client.get("/api/bookings")
    # Without login, should return 401 Unauthorized
    assert response.status_code in [401, 302]


def test_api_root_returns_200(client):
    """API root should be accessible."""
    response = client.get("/api/users")
    assert response.status_code == 200
    