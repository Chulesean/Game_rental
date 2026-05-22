from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Game, Player, PlayerGame

players_bp = Blueprint("players", __name__)


@players_bp.route("/players")
def listing():
    """Browse all available players, with optional filters."""
    skill = request.args.get("skill")       # e.g. ?skill=advanced
    game_id = request.args.get("game_id")   # e.g. ?game_id=3

    query = Player.query.filter_by(is_available=True)

    if skill:
        query = query.filter_by(skill_level=skill)

    if game_id:
        query = query.join(PlayerGame).filter(PlayerGame.game_id == game_id)

    players = query.order_by(Player.fee_per_hour).all()
    games = Game.query.order_by(Game.title).all()   # for the filter dropdown

    return render_template("players/listing.html", players=players, games=games)


@players_bp.route("/players/<int:player_id>")
def player_detail(player_id):
    """Full profile of a single player."""
    player = Player.query.get_or_404(player_id)
    return render_template("players/player_detail.html", player=player)


@players_bp.route("/players/become", methods=["GET", "POST"])
@login_required
def become_player():
    """Let a regular user create a player profile."""
    if current_user.player_profile:
        flash("You already have a player profile.", "info")
        return redirect(url_for("players.edit_profile"))

    if request.method == "POST":
        bio = request.form.get("bio", "").strip()
        fee = request.form.get("fee_per_hour", 0)
        skill = request.form.get("skill_level", "intermediate")
        game_ids = request.form.getlist("game_ids")   # multi-select

        player = Player(
            user_id=current_user.id,
            bio=bio,
            fee_per_hour=float(fee),
            skill_level=skill,
        )
        db.session.add(player)
        db.session.flush()  # get player.id before committing

        for gid in game_ids:
            pg = PlayerGame(player_id=player.id, game_id=int(gid))
            db.session.add(pg)

        db.session.commit()
        flash("Player profile created!", "success")
        return redirect(url_for("players.player_detail", player_id=player.id))

    games = Game.query.order_by(Game.title).all()
    return render_template("players/become_player.html", games=games)


@players_bp.route("/players/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    """Edit the current user's player profile."""
    player = current_user.player_profile

    if not player:
        flash("You don't have a player profile yet.", "warning")
        return redirect(url_for("players.become_player"))

    if request.method == "POST":
        player.bio = request.form.get("bio", "").strip()
        player.fee_per_hour = float(request.form.get("fee_per_hour", player.fee_per_hour))
        player.skill_level = request.form.get("skill_level", player.skill_level)
        player.is_available = "is_available" in request.form

        # Update games: remove old, add new
        PlayerGame.query.filter_by(player_id=player.id).delete()
        for gid in request.form.getlist("game_ids"):
            pg = PlayerGame(player_id=player.id, game_id=int(gid))
            db.session.add(pg)

        db.session.commit()
        flash("Player profile updated.", "success")
        return redirect(url_for("players.player_detail", player_id=player.id))

    games = Game.query.order_by(Game.title).all()
    return render_template("players/edit_profile.html", player=player, games=games)
