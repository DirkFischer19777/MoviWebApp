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
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    name = request.form.get('name')
    if not name:
        flash("User name cannot be empty!", "error")
        return redirect(url_for('home'))

    # Check for duplicate user
    existing_users = data_manager.get_users()
    if any(u.name.lower() == name.lower() for u in existing_users):
        flash(f"User '{name}' already exists!", "error")
        return redirect(url_for('home'))

    try:
        data_manager.create_user(name)
        flash(f"User '{name}' added successfully!", "success")
    except Exception as e:
        flash(f"Error adding user: {str(e)}", "error")

    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def user_movies(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            try:
                movie = data_manager.add_movie(user_id, title)
                if movie:
                    flash(f'Movie "{movie.name}" added!', "success")
                else:
                    flash(f'Movie "{title}" not found via OMDb API.', "error")
            except Exception as e:
                flash(f"Error adding movie: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))

    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    new_title = request.form.get('new_title')
    if new_title:
        try:
            data_manager.update_movie(movie_id, new_title)
            flash("Movie updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating movie: {str(e)}", "error")
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(movie_id)
        flash("Movie deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting movie: {str(e)}", "error")
    return redirect(url_for('user_movies', user_id=user_id))


# -------------------------------------------
# Error handlers
# -------------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


# -------------------------------------------
# Run Flask app
# -------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
