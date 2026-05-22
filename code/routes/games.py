from extensions import db
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from models import Game

games_bp = Blueprint("games", __name__)


@games_bp.route("/games")
def listing():
    """Browse all available games."""
    genre = request.args.get("genre")
    platform = request.args.get("platform")

    query = Game.query

    if genre:
        query = query.filter_by(genre=genre)

    if platform:
        query = query.filter_by(platform=platform)

    games = query.order_by(Game.title).all()

    # Unique genre and platform values for filter dropdowns
    genres = db.session.query(Game.genre).distinct().order_by(Game.genre).all()
    platforms = db.session.query(Game.platform).distinct().order_by(Game.platform).all()

    return render_template(
        "games/listing.html",
        games=games,
        genres=[g[0] for g in genres if g[0]],
        platforms=[p[0] for p in platforms if p[0]],
    )


@games_bp.route("/games/<int:game_id>")
def game_detail(game_id):
    """Detail page: game info + list of available players for this game."""
    game = Game.query.get_or_404(game_id)
    # Players who offer this game and are available
    available_players = [pg.player for pg in game.players if pg.player.is_available]
    return render_template(
        "games/game_detail.html", game=game, players=available_players
    )


@games_bp.route("/games/new", methods=["GET", "POST"])
@login_required
def new_game():
    """Add a new game to the catalogue (any logged-in user can suggest one)."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        genre = request.form.get("genre", "").strip()
        platform = request.form.get("platform", "").strip()

        if not title:
            flash("Game title is required.", "danger")
            return render_template("games/game_form.html")

        if Game.query.filter_by(title=title).first():
            flash("A game with that title already exists.", "warning")
            return render_template("games/game_form.html")

        game = Game(title=title, genre=genre or None, platform=platform or None)
        db.session.add(game)
        db.session.commit()

        flash(f'"{title}" added to the catalogue.', "success")
        return redirect(url_for("games.game_detail", game_id=game.id))

    return render_template("games/game_form.html")
