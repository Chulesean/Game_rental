import os


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Suppress deprecation warning
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    """Local development — SQLite for simplicity, debug on."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///dev.db"
    )


class TestingConfig(Config):
    """Unit tests — in-memory SQLite, CSRF disabled for test client."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False     # Allows test client to POST without tokens


class ProductionConfig(Config):
    """Production — PostgreSQL via DATABASE_URL env var (set in .env)."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Safety check: crash early if secrets are missing in production
    @classmethod
    def validate(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable is not set")
        if cls.SECRET_KEY == "change-me-in-production":
            raise ValueError("SECRET_KEY must be changed for production")


# Map string names → classes (used in flask_app.py and tests)
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
