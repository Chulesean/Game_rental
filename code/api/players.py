from flask import Blueprint, jsonify, request

from models import Player, PlayerGame

api_players_bp = Blueprint("api_players", __name__)


def _player_dict(p):
    """Serialize a Player to a dict."""
    return {
        "id": p.id,
        "user_id": p.user_id,
        "username": p.user.username,
        "bio": p.bio,
        "fee_per_hour": p.fee_per_hour,
        "skill_level": p.skill_level,
        "is_available": p.is_available,
        "games": [
            {
                "game_id": pg.game_id,
                "title": pg.game.title,
                "skill_level": pg.skill_level,
            }
            for pg in p.games
        ],
    }


@api_players_bp.route("/players")
def get_players():
    """GET /api/players — list players, optional ?skill= and ?game_id= filters."""
    skill = request.args.get("skill")
    game_id = request.args.get("game_id")

    query = Player.query.filter_by(is_available=True)

    if skill:
        query = query.filter_by(skill_level=skill)

    if game_id:
        query = query.join(PlayerGame).filter(PlayerGame.game_id == int(game_id))

    players = query.order_by(Player.fee_per_hour).all()
    return jsonify([_player_dict(p) for p in players])


@api_players_bp.route("/players/<int:player_id>")
def get_player(player_id):
    """GET /api/players/<id> — single player."""
    p = Player.query.get_or_404(player_id)
    return jsonify(_player_dict(p))
