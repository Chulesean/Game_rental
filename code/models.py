from datetime import datetime

from flask_login import UserMixin

from extensions import db


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    """
    Represents any registered account.
    A user can be a CLIENT (looking to hire), a PLAYER (available for hire),
    or both at the same time.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    player_profile = db.relationship("Player", back_populates="user", uselist=False)
    bookings_as_client = db.relationship(
        "Booking", foreign_keys="Booking.client_id", back_populates="client"
    )
    reviews_written = db.relationship(
        "Review", foreign_keys="Review.reviewer_id", back_populates="reviewer"
    )

    def __repr__(self):
        return f"<User {self.username}>"


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(db.Model):
    """
    A user who is available for hire.
    Linked 1-to-1 with User; stores hire-specific info.
    """

    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bio = db.Column(db.Text)
    fee_per_hour = db.Column(db.Float, nullable=False)             # e.g. 5.00 €/hr
    skill_level = db.Column(
        db.Enum("beginner", "intermediate", "advanced", "pro", name="skill_levels"),
        nullable=False,
        default="intermediate",
    )
    is_available = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship("User", back_populates="player_profile")
    games = db.relationship("PlayerGame", back_populates="player")
    bookings = db.relationship(
        "Booking", foreign_keys="Booking.player_id", back_populates="player"
    )

    def __repr__(self):
        return f"<Player user_id={self.user_id} skill={self.skill_level}>"


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------
class Game(db.Model):
    """A game that players can be hired to play."""

    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, nullable=False)
    genre = db.Column(db.String(64))                               # e.g. FPS, RPG
    platform = db.Column(db.String(64))                            # e.g. PC, PS5

    # Relationships
    players = db.relationship("PlayerGame", back_populates="game")
    bookings = db.relationship("Booking", back_populates="game")

    def __repr__(self):
        return f"<Game {self.title}>"


# ---------------------------------------------------------------------------
# PlayerGame  (association: which games a player offers)
# ---------------------------------------------------------------------------
class PlayerGame(db.Model):
    """Many-to-many between Player and Game with extra info per pair."""

    __tablename__ = "player_games"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    skill_level = db.Column(                                       # Per-game skill
        db.Enum("beginner", "intermediate", "advanced", "pro", name="skill_levels"),
        nullable=False,
        default="intermediate",
    )

    # Relationships
    player = db.relationship("Player", back_populates="games")
    game = db.relationship("Game", back_populates="players")

    def __repr__(self):
        return f"<PlayerGame player={self.player_id} game={self.game_id}>"


# ---------------------------------------------------------------------------
# Booking
# ---------------------------------------------------------------------------
class Booking(db.Model):
    """
    A session booked by a client with a player for a specific game.
    Tracks time slot, fee agreed, and current status.
    """

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    total_fee = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.Enum(
            "pending", "accepted", "completed", "cancelled", "denied", name="booking_statuses"
        ),
        default="pending",
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    client = db.relationship(
        "User", foreign_keys=[client_id], back_populates="bookings_as_client"
    )
    player = db.relationship(
        "Player", foreign_keys=[player_id], back_populates="bookings"
    )
    game = db.relationship("Game", back_populates="bookings")
    review = db.relationship("Review", back_populates="booking", uselist=False)

    def __repr__(self):
        return f"<Booking id={self.id} status={self.status}>"


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------
class Review(db.Model):
    """
    A review left by a client after a completed booking.
    One review per booking, max.
    """

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.id"), unique=True, nullable=False
    )
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)                 # 1–5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    booking = db.relationship("Booking", back_populates="review")
    reviewer = db.relationship(
        "User", foreign_keys=[reviewer_id], back_populates="reviews_written"
    )

    def __repr__(self):
        return f"<Review booking={self.booking_id} rating={self.rating}>"
    