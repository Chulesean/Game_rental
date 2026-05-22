from flask import Blueprint, jsonify, request
from models import Game

api_games_bp = Blueprint("api_games", __name__)


def _game_dict(g):
    """Serialize a Game to a dict."""
    return {
        "id": g.id,
        "title": g.title,
        "genre": g.genre,
        "platform": g.platform,
        "player_count": len(g.players),
    }


@api_games_bp.route("/games")
def get_games():
    """GET /api/games — list all games, optional ?genre= and ?platform= filters."""
    genre = request.args.get("genre")
    platform = request.args.get("platform")

    query = Game.query

    if genre:
        query = query.filter_by(genre=genre)

    if platform:
        query = query.filter_by(platform=platform)

    games = query.order_by(Game.title).all()
    return jsonify([_game_dict(g) for g in games])


@api_games_bp.route("/games/<int:game_id>")
def get_game(game_id):
    """GET /api/games/<id> — single game with available players."""
    g = Game.query.get_or_404(game_id)
    data = _game_dict(g)
    data["players"] = [
        {
            "player_id": pg.player_id,
            "username": pg.player.user.username,
            "skill_level": pg.skill_level,
            "fee_per_hour": pg.player.fee_per_hour,
        }
        for pg in g.players
        if pg.player.is_available
    ]
    return jsonify(data)
