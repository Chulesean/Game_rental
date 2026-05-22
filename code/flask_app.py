import os

from flask import Flask

from config import config_map
from extensions import db, login_manager

# Extensions declared here so models.py can import them without circular imports


def create_app(config_name: str = None) -> Flask:
    """
    App factory — creates and configures the Flask application.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # --- Load config ---
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_map[config_name])

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Register blueprints (HTML routes) ---
    from routes.auth import auth_bp
    from routes.bookings import bookings_bp
    from routes.games import games_bp
    from routes.players import players_bp
    from routes.reviews import reviews_bp
    from routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(reviews_bp)

    # --- Register API blueprints (JSON endpoints under /api) ---
    from api.bookings import api_bookings_bp
    from api.games import api_games_bp
    from api.players import api_players_bp
    from api.reviews import api_reviews_bp
    from api.users import api_users_bp

    app.register_blueprint(api_users_bp, url_prefix="/api")
    app.register_blueprint(api_players_bp, url_prefix="/api")
    app.register_blueprint(api_games_bp, url_prefix="/api")
    app.register_blueprint(api_bookings_bp, url_prefix="/api")
    app.register_blueprint(api_reviews_bp, url_prefix="/api")

    return app


# --- User loader required by Flask-Login ---
@login_manager.user_loader
def load_user(user_id: int):
    from models import User
    return User.query.get(int(user_id))


# --- Entry point for local development ---
if __name__ == "__main__":
    app = create_app("development")
    
    # Tạo database tables trong app context
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified!")
    
    app.run(debug=True)
