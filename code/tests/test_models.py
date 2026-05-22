"""Simple tests for database models."""


def test_create_user(db_session):
    """Test creating a user works."""
    from models import User
    from werkzeug.security import generate_password_hash

    user = User(
        username="newuser",
        email="new@example.com",
        password_hash=generate_password_hash("secret"),
    )
    db_session.session.add(user)
    db_session.session.commit()

    assert user.id is not None
    assert user.username == "newuser"


def test_create_game(db_session):
    """Test creating a game works."""
    from models import Game

    game = Game(title="Valorant", genre="FPS", platform="PC")
    db_session.session.add(game)
    db_session.session.commit()

    assert game.id is not None
    assert game.title == "Valorant"
