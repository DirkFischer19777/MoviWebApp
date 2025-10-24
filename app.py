from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db
import os
from dotenv import load_dotenv

# -------------------------------------------
# Load .env file
# -------------------------------------------
"""Load environment variables from the .env file.
This allows sensitive data such as API keys to be stored securely outside the codebase.
"""
load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# -------------------------------------------
# Flask application setup
# -------------------------------------------
"""Initialize the Flask web application and configure the database connection.
The app uses SQLite for local storage and integrates SQLAlchemy as the ORM layer.
"""
app = Flask(__name__)

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
"""Define all web routes for user and movie management.
Each route corresponds to a specific CRUD operation for Users or Movies.
"""
@app.route('/')
def home():
    """Display the homepage listing all users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Create a new user based on submitted form data."""
    name = request.form.get('name')
    data_manager.create_user(name)
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    """Display all movies associated with a specific user."""
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a new movie to the selected user's movie list.
    Fetches additional details from the OMDb API if available.
    """
    title = request.form.get('title')
    data_manager.add_movie(user_id, title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update the title of an existing movie for a specific user."""
    new_title = request.form.get('new_title')
    data_manager.update_movie(movie_id, new_title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie from a user's movie list."""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))



# -------------------------------------------
# Run the Flask app
# -------------------------------------------
"""Start the Flask development server.
Ensures the database tables are created before launching the app.
"""
if __name__ == '__main__':
    # Ensure the database is created before running the app
    with app.app_context():
        db.create_all()

    # Run the Flask development server
    app.run(debug=True)
