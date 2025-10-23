from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db
import os

# -------------------------------------------
# Flask application setup
# -------------------------------------------

app = Flask(__name__)

# Base directory for database path
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with Flask app
db.init_app(app)

# Initialize DataManager
data_manager = DataManager()

# -------------------------------------------
# Routes
# -------------------------------------------

@app.route('/')
def home():
    """Homepage showing all users"""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user"""
    name = request.form.get('name')
    data_manager.create_user(name)
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    """List all movies for a specific user"""
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """Add a movie to user's list"""
    title = request.form.get('title')
    data_manager.add_movie(user_id, title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update a movie title"""
    new_title = request.form.get('new_title')
    data_manager.update_movie(movie_id, new_title)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Delete a movie"""
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))



# -------------------------------------------
# Run the Flask app
# -------------------------------------------
if __name__ == '__main__':
    # Ensure the database is created before running the app
    with app.app_context():
        db.create_all()

    # Run the Flask development server
    app.run(debug=True)
