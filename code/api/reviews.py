from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from extensions import db
from models import Booking, Review

api_reviews_bp = Blueprint("api_reviews", __name__)


def _review_dict(r):
    """Serialize a Review to a dict."""
    return {
        "id": r.id,
        "booking_id": r.booking_id,
        "reviewer_id": r.reviewer_id,
        "reviewer_username": r.reviewer.username,
        "player_id": r.booking.player_id,
        "player_username": r.booking.player.user.username,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat(),
    }


@api_reviews_bp.route("/reviews/<int:review_id>")
def get_review(review_id):
    """GET /api/reviews/<id> — single review."""
    review = Review.query.get_or_404(review_id)
    return jsonify(_review_dict(review))


@api_reviews_bp.route("/players/<int:player_id>/reviews")
def get_player_reviews(player_id):
    """GET /api/players/<id>/reviews — all reviews for a player."""
    reviews = (
        Review.query
        .join(Booking)
        .filter(Booking.player_id == player_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    avg_rating = (
        round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else None
    )
    return jsonify({
        "player_id": player_id,
        "review_count": len(reviews),
        "average_rating": avg_rating,
        "reviews": [_review_dict(r) for r in reviews],
    })


@api_reviews_bp.route("/reviews", methods=["POST"])
@login_required
def create_review():
    """POST /api/reviews — submit a review for a completed booking."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    required = ["booking_id", "rating"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    booking = Booking.query.get_or_404(data["booking_id"])

    if booking.client_id != current_user.id:
        return jsonify({"error": "You can only review your own bookings."}), 403

    if booking.status != "completed":
        return jsonify({"error": "You can only review completed bookings."}), 400

    if booking.review:
        return jsonify({"error": "You have already reviewed this booking."}), 409

    rating = data["rating"]
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be an integer between 1 and 5."}), 400

    review = Review(
        booking_id=booking.id,
        reviewer_id=current_user.id,
        rating=rating,
        comment=data.get("comment", "").strip() or None,
    )
    db.session.add(review)
    db.session.commit()

    return jsonify(_review_dict(review)), 201
