from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Booking, Player

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/bookings")
@login_required
def my_bookings():
    """List all bookings for the current user (as client)."""
    bookings = (
        Booking.query.filter_by(client_id=current_user.id)
        .order_by(Booking.start_time.desc())
        .all()
    )
    return render_template("bookings/my_bookings.html", bookings=bookings)


@bookings_bp.route("/bookings/new", methods=["GET", "POST"])
@login_required
def create():
    """Book a player for a game session."""
    player_id = request.args.get("player_id") or request.form.get("player_id")
    player = Player.query.get_or_404(player_id)

    # PREVENT SELF-BOOKING
    if current_user.player_profile and current_user.player_profile.id == player.id:
        flash("You cannot book yourself! Please choose a different player.", "danger")
        return redirect(url_for("players.player_detail", player_id=player.id))


    if request.method == "POST":
        game_id = request.form.get("game_id")
        start_str = request.form.get("start_time")
        end_str = request.form.get("end_time")

        # Parse datetimes
        try:
            start_time = datetime.fromisoformat(start_str)
            end_time = datetime.fromisoformat(end_str)
        except (ValueError, TypeError):
            flash("Invalid date/time format.", "danger")
            return render_template("bookings/create.html", player=player)

        if end_time <= start_time:
            flash("End time must be after start time.", "danger")
            return render_template("bookings/create.html", player=player)

        # Calculate fee: hours × player rate
        hours = (end_time - start_time).total_seconds() / 3600
        total_fee = round(hours * player.fee_per_hour, 2)

        # Check player has no overlapping confirmed bookings
        overlap = Booking.query.filter(
            Booking.player_id == player.id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        ).first()

        if overlap:
            flash("That player is already booked for that time slot.", "danger")
            return render_template("bookings/create.html", player=player)

        booking = Booking(
            client_id=current_user.id,
            player_id=player.id,
            game_id=int(game_id),
            start_time=start_time,
            end_time=end_time,
            total_fee=total_fee,
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()

        flash(f"Booking requested! Total fee: €{total_fee:.2f}", "success")
        return redirect(url_for("bookings.my_bookings"))

    return render_template("bookings/create.html", player=player)


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel(booking_id):
    """Cancel a pending or confirmed booking (client only)."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.client_id != current_user.id:
        flash("You can only cancel your own bookings.", "danger")
        return redirect(url_for("bookings.my_bookings"))

    if booking.status not in ("pending", "confirmed"):
        flash("This booking cannot be cancelled.", "warning")
        return redirect(url_for("bookings.my_bookings"))

    booking.status = "cancelled"
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("bookings.my_bookings"))


@bookings_bp.route("/bookings/<int:booking_id>/accept", methods=["POST"])
@login_required
def accept_booking(booking_id):
    """Player accepts a pending booking."""
    booking = Booking.query.get_or_404(booking_id)

    # Check if current user is the player
    if not current_user.player_profile:
        flash("Only players can accept bookings.", "danger")
        return redirect(url_for("users.dashboard"))

    if booking.player_id != current_user.player_profile.id:
        flash("You can only accept your own bookings.", "danger")
        return redirect(url_for("users.dashboard"))

    if booking.status != "pending":
        flash("Only pending bookings can be accepted.", "warning")
        return redirect(url_for("users.dashboard"))

    # Accept the booking
    booking.status = "accepted"
    db.session.commit()

    flash(f"Booking #{booking.id} has been ACCEPTED! The client has been notified.", "success")
    return redirect(url_for("users.dashboard"))


@bookings_bp.route("/bookings/<int:booking_id>/deny", methods=["POST"])
@login_required
def deny_booking(booking_id):
    """Player denies a pending booking."""
    booking = Booking.query.get_or_404(booking_id)

    # Check if current user is the player
    if not current_user.player_profile:
        flash("Only players can deny bookings.", "danger")
        return redirect(url_for("users.dashboard"))

    if booking.player_id != current_user.player_profile.id:
        flash("You can only deny your own bookings.", "danger")
        return redirect(url_for("users.dashboard"))

    if booking.status != "pending":
        flash("Only pending bookings can be denied.", "warning")
        return redirect(url_for("users.dashboard"))

    # Deny the booking
    booking.status = "denied"
    db.session.commit()

    flash(f"Booking #{booking.id} has been DENIED. The client has been notified.", "info")
    return redirect(url_for("users.dashboard"))