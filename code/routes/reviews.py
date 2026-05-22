from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Booking, Review

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/reviews/new/<int:booking_id>", methods=["GET", "POST"])
@login_required
def new_review(booking_id):
    """Write a review for a completed booking."""
    booking = Booking.query.get_or_404(booking_id)

    # Only the client of this booking can review it
    if booking.client_id != current_user.id:
        flash("You can only review your own bookings.", "danger")
        return redirect(url_for("bookings.my_bookings"))

    if booking.status != "completed":
        flash("You can only review completed bookings.", "warning")
        return redirect(url_for("bookings.my_bookings"))

    if booking.review:
        flash("You have already reviewed this booking.", "info")
        return redirect(url_for("reviews.review_detail", review_id=booking.review.id))

    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment", "").strip()

        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            flash("Rating must be a number between 1 and 5.", "danger")
            return render_template("reviews/review_form.html", booking=booking)

        review = Review(
            booking_id=booking.id,
            reviewer_id=current_user.id,
            rating=int(rating),
            comment=comment or None,
        )
        db.session.add(review)
        db.session.commit()

        flash("Review submitted. Thanks!", "success")
        return redirect(url_for("bookings.my_bookings"))

    return render_template("reviews/review_form.html", booking=booking)


@reviews_bp.route("/reviews/<int:review_id>")
def review_detail(review_id):
    """Public view of a single review."""
    review = Review.query.get_or_404(review_id)
    return render_template("reviews/review_detail.html", review=review)


@reviews_bp.route("/players/<int:player_id>/reviews")
def player_reviews(player_id):
    """All reviews for a given player."""
    reviews = (
        Review.query
        .join(Booking)
        .filter(Booking.player_id == player_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return render_template(
        "reviews/player_reviews.html", reviews=reviews, player_id=player_id
    )
