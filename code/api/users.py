from flask import Blueprint, jsonify
from models import User

api_users_bp = Blueprint("api_users", __name__)


@api_users_bp.route("/users")
def get_users():
    """GET /api/users — list all users."""
    users = User.query.order_by(User.username).all()
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at.isoformat(),
                "is_player": u.player_profile is not None,
            }
            for u in users
        ]
    )


@api_users_bp.route("/users/<int:user_id>")
def get_user(user_id):
    """GET /api/users/<id> — single user."""
    u = User.query.get_or_404(user_id)
    return jsonify(
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "created_at": u.created_at.isoformat(),
            "is_player": u.player_profile is not None,
        }
    )
