from datetime import datetime

from extensions import db
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from models import Booking, Player, User
from werkzeug.security import generate_password_hash

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


@users_bp.route("/dashboard")
@login_required
def dashboard():
    """Shows the user's upcoming bookings and quick stats."""

    # Client's bookings (as customer)
    upcoming_as_client = (
        Booking.query.filter_by(client_id=current_user.id)
        .filter(Booking.status.in_(["pending", "accepted"]))
        .order_by(Booking.start_time)
        .all()
    )
    past_as_client = (
        Booking.query.filter_by(client_id=current_user.id)
        .filter(Booking.status == "completed")
        .order_by(Booking.start_time.desc())
        .limit(5)
        .all()
    )

    # Player's pending bookings (as service provider)
    pending_as_player = []
    if current_user.player_profile:
        pending_as_player = (
            Booking.query.filter_by(player_id=current_user.player_profile.id)
            .filter(Booking.status == "pending")
            .order_by(Booking.start_time)
            .all()
        )

    # Player's accepted bookings
    accepted_as_player = []
    if current_user.player_profile:
        accepted_as_player = (
            Booking.query.filter_by(player_id=current_user.player_profile.id)
            .filter(Booking.status == "accepted")
            .order_by(Booking.start_time)
            .all()
        )

    # Auto-complete past accepted bookings
    if current_user.player_profile:
        past_accepted = Booking.query.filter(
            Booking.player_id == current_user.player_profile.id,
            Booking.status == "accepted",
            Booking.end_time < datetime.utcnow(),
        ).all()

        for booking in past_accepted:
            booking.status = "completed"
        db.session.commit()

    return render_template(
        "users/dashboard.html",
        upcoming_as_client=upcoming_as_client,
        past_as_client=past_as_client,
        pending_as_player=pending_as_player,
        accepted_as_player=accepted_as_player,
    )


@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """View and edit the current user's profile."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        new_password = request.form.get("new_password", "")

        if not username or not email:
            flash("Username and email are required.", "danger")
            return render_template("users/profile.html")

        # Check uniqueness only if the value changed
        if username != current_user.username:
            if User.query.filter_by(username=username).first():
                flash("Username already taken.", "danger")
                return render_template("users/profile.html")

        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash("Email already registered.", "danger")
                return render_template("users/profile.html")

        current_user.username = username
        current_user.email = email

        if new_password:
            current_user.password_hash = generate_password_hash(new_password)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("users.profile"))

    return render_template("users/profile.html")


@users_bp.route("/users/<int:user_id>")
def public_profile(user_id):
    """Public view of any user's profile."""
    user = User.query.get_or_404(user_id)
    player = Player.query.filter_by(user_id=user_id).first()
    return render_template("users/profile.html", user=user, player=player)


@users_bp.route("/search")
def search():
    """Search for players and games."""
    from models import Game, Player

    query = request.args.get("q", "").strip()

    if query:
        # Tìm kiếm player theo username
        players = (
            Player.query.join(User)
            .filter(User.username.ilike(f"%{query}%"))
            .filter(Player.is_available)
            .all()
        )

        # Tìm kiếm game theo title
        games = Game.query.filter(Game.title.ilike(f"%{query}%")).all()
    else:
        players = []
        games = []

    # Lấy dữ liệu cho trang chủ (featured và popular)
    featured_players = Player.query.filter_by(is_available=True).limit(6).all()
    popular_games = Game.query.limit(6).all()

    return render_template(
        "search.html",
        search_query=query,
        players=players,
        games=games,
        featured_players=featured_players,
        popular_games=popular_games,
    )
