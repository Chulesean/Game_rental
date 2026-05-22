"""Shared fixtures for tests."""

import pytest
from extensions import db
from flask_app import create_app
from models import Game, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Database session for tests."""
    with app.app_context():
        yield db


@pytest.fixture
def sample_user(db_session):
    """Create a sample user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=generate_password_hash("password123"),
    )
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def sample_game(db_session):
    """Create a sample game."""
    game = Game(title="Test Game", genre="RPG", platform="PC")
    db_session.session.add(game)
    db_session.session.commit()
    return game
