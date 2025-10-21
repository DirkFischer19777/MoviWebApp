from flask import Flask
from data_manager import DataManager
from models import db, Movie
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
    """Simple test route to verify app is running"""
    return "Welcome to MoviWeb App!"


# -------------------------------------------
# Run the Flask app
# -------------------------------------------
if __name__ == '__main__':
    # Ensure the database is created before running the app
    with app.app_context():
        db.create_all()

    # Run the Flask development server
    app.run(debug=True)
