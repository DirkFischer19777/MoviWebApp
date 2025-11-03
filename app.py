from flask import Flask, request, redirect, url_for, render_template, flash
from data_manager import DataManager
from models import db, User, Movie
import os
from dotenv import load_dotenv
import requests

# -------------------------------------------
# Load environment variables
# -------------------------------------------
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# -------------------------------------------
# Flask app setup
# -------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "devkey")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager(omdb_api_key=OMDB_API_KEY)


# -------------------------------------------
# Routes
# -------------------------------------------

@app.route('/')
def home():
    """Display all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user with duplicate name check."""
    name = request.form.get('name')

    if not name.strip():
        flash("Username cannot be empty.", "error")
        return redirect(url_for('home'))

    existing_user = User.query.filter_by(name=name).first()
    if existing_user:
        flash(f'User "{name}" already exists!', 'error')
        return redirect(url_for('home'))

    data_manager.create_user(name)
    flash(f'User "{name}" created successfully!', 'success')
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    """Display all movies for a user."""
    user = User.query.get_or_404(user_id)
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies/add', methods=['POST'])
def add_movie(user_id):
    """Add a new movie to a user's list, prevent duplicates, and handle OMDb errors."""
    title = request.form.get('title')
    user = User.query.get_or_404(user_id)

    if not title.strip():
        flash("Movie title cannot be empty.", "error")
        return redirect(url_for('user_movies', user_id=user_id))

    existing_movie = Movie.query.filter_by(title=title, user_id=user_id).first()
    if existing_movie:
        flash(f'Movie "{title}" already exists for {user.name}!', 'error')
        return redirect(url_for('user_movies', user_id=user_id))

    try:
        response = requests.get(f'https://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}')
        data = response.json()

        if data.get("Response") == "True":
            movie = Movie(
                title=data.get("Title"),
                year=data.get("Year"),
                director=data.get("Director"),
                rating=data.get("imdbRating"),
                poster_url=data.get("Poster"),
                user_id=user_id
            )
            db.session.add(movie)
            db.session.commit()
            flash(f'Movie "{data.get("Title")}" added successfully!', 'success')
        else:
            flash(f'Movie "{title}" not found on OMDb.', 'error')

    except Exception as e:
        flash(f"Error while fetching movie data: {e}", "error")

    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update a movie title."""
    new_title = request.form.get('new_title')

    if not new_title.strip():
        flash("New title cannot be empty.", "error")
        return redirect(url_for('user_movies', user_id=user_id))

    movie = Movie.query.get_or_404(movie_id)
    movie.title = new_title
    db.session.commit()
    flash(f'Movie title updated to "{new_title}".', 'success')
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie with error handling."""
    try:
        movie = Movie.query.get_or_404(movie_id)
        db.session.delete(movie)
        db.session.commit()
        flash(f'Movie "{movie.title}" deleted successfully.', 'success')
    except Exception as e:
        flash(f"Error deleting movie: {e}", "error")
    return redirect(url_for('user_movies', user_id=user_id))


# -------------------------------------------
# Error Handling
# -------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Custom 500 page."""
    return render_template('500.html'), 500


# -------------------------------------------
# Run app
# -------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
