from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance.
# This will be initialized in app.py using db.init_app(app)
db = SQLAlchemy()


# ---------- User Model ----------
class User(db.Model):
    """
    Represents a user in the MoviWeb application.
    Each user has a unique ID, a name, and can have multiple movies.
    """
    __tablename__ = "user"  # Explicit table name for clarity

    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    name = db.Column(db.String(100), nullable=False)  # User name

    # Relationship: one user -> many movies
    movies = db.relationship(
        "Movie",
        backref="user",               # Allows accessing user from movie.user
        cascade="all, delete-orphan"  # Delete movies when user is deleted
    )

    def __repr__(self):
        return f"<User id={self.id}, name={self.name}>"


# ---------- Movie Model ----------
class Movie(db.Model):
    """
    Represents a movie linked to a specific user.
    Each movie stores basic details like title, director, year, and poster URL.
    """
    __tablename__ = "movie"  # Explicit table name for clarity

    id = db.Column(db.Integer, primary_key=True)  # Unique movie ID
    name = db.Column(db.String(255), nullable=False)  # Movie title
    director = db.Column(db.String(255))  # Movie director
    year = db.Column(db.Integer)  # Release year
    poster_url = db.Column(db.String(1024))  # Poster image URL

    # Foreign key linking to the User table
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"<Movie id={self.id}, name={self.name}, user_id={self.user_id}>"
