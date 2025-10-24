from flask import Flask, request, redirect, url_for, render_template, flash
from data_manager import DataManager
from models import db, User, Movie
import os
from dotenv import load_dotenv

# -------------------------------------------
# Load .env file
# -------------------------------------------
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "devkey")

# -------------------------------------------
# Flask application setup
# -------------------------------------------
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Base directory for database path
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with Flask app
db.init_app(app)

# Initialize DataManager
data_manager = DataManager(omdb_api_key=OMDB_API_KEY)

# -------------------------------------------
# Routes
# -------------------------------------------
@app.route('/')
def home():
    """Display the homepage listing all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Create a new user based on submitted form data."""
    name = request.form.get('name')
    if name:
        data_manager.create_user(name)
        flash(f'User "{name}" created!', 'success')
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def user_movies(user_id):
    """Display all movies for a user and handle adding new movies."""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            movie = data_manager.add_movie(user_id, title)
            if movie:
                flash(f'Movie "{movie.name}" added!', 'success')
            else:
                flash(f'Movie "{title}" could not be added.', 'error')
        return redirect(url_for('user_movies', user_id=user_id))

    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user=user)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update the title of an existing movie for a specific user."""
    new_title = request.form.get('new_title')
    if new_title:
        data_manager.update_movie(movie_id, new_title)
        flash(f'Movie updated to "{new_title}"!', 'success')
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's movie list."""
    success = data_manager.delete_movie(movie_id)
    if success:
        flash('Movie deleted successfully.', 'success')
    else:
        flash('Movie could not be deleted.', 'error')
    return redirect(url_for('user_movies', user_id=user_id))


# -------------------------------------------
# Run the Flask app
# -------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
