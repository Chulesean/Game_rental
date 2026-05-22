from datetime import datetime

from extensions import db
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import Booking, Player

api_bookings_bp = Blueprint("api_bookings", __name__)


def _booking_dict(b):
    """Serialize a Booking to a dict."""
    return {
        "id": b.id,
        "client_id": b.client_id,
        "client_username": b.client.username,
        "player_id": b.player_id,
        "player_username": b.player.user.username,
        "game_id": b.game_id,
        "game_title": b.game.title,
        "start_time": b.start_time.isoformat(),
        "end_time": b.end_time.isoformat(),
        "total_fee": b.total_fee,
        "status": b.status,
        "created_at": b.created_at.isoformat(),
    }


@api_bookings_bp.route("/bookings")
@login_required
def get_bookings():
    """GET /api/bookings — all bookings for the current user."""
    bookings = (
        Booking.query.filter_by(client_id=current_user.id)
        .order_by(Booking.start_time.desc())
        .all()
    )
    return jsonify([_booking_dict(b) for b in bookings])


@api_bookings_bp.route("/bookings", methods=["POST"])
@login_required
def create_booking():
    """POST /api/bookings — create a new booking."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    required = ["player_id", "game_id", "start_time", "end_time"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    player = Player.query.get_or_404(data["player_id"])

    try:
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.fromisoformat(data["end_time"])
    except ValueError:
        return jsonify({"error": "Invalid datetime format. Use ISO 8601."}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time must be after start_time."}), 400

    # Check for overlapping bookings
    overlap = Booking.query.filter(
        Booking.player_id == player.id,
        Booking.status.in_(["pending", "confirmed"]),
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    ).first()

    if overlap:
        return jsonify({"error": "Player is already booked for that time slot."}), 409

    hours = (end_time - start_time).total_seconds() / 3600
    total_fee = round(hours * player.fee_per_hour, 2)

    booking = Booking(
        client_id=current_user.id,
        player_id=player.id,
        game_id=int(data["game_id"]),
        start_time=start_time,
        end_time=end_time,
        total_fee=total_fee,
        status="pending",
    )
    db.session.add(booking)
    db.session.commit()

    return jsonify(_booking_dict(booking)), 201


@api_bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    """POST /api/bookings/<id>/cancel — cancel a pending or confirmed booking."""
    booking = Booking.query.get_or_404(booking_id)

    if booking.client_id != current_user.id:
        return jsonify({"error": "You can only cancel your own bookings."}), 403

    if booking.status not in ("pending", "confirmed"):
        return jsonify({"error": "This booking cannot be cancelled."}), 400

    booking.status = "cancelled"
    db.session.commit()

    return jsonify({"message": "Booking cancelled.", "booking": _booking_dict(booking)})
