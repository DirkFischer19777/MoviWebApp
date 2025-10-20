import requests
from models import db, User, Movie


class DataManager:
    """
    DataManager provides an abstraction layer for interacting with the database.
    It supports basic CRUD operations for both User and Movie models,
    and can fetch movie information automatically from the OMDb API.
    """

    def __init__(self, omdb_api_key: str = None):
        """
        Initialize the DataManager.
        :param omdb_api_key: Optional OMDb API key for fetching movie data.
        """
        self.omdb_api_key = omdb_api_key

    # ---------- USER METHODS ----------

    def create_user(self, name: str) -> User:
        """Create a new user and add it to the database."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def get_users(self) -> list[User]:
        """Retrieve all users from the database."""
        return User.query.order_by(User.name).all()

    # ---------- MOVIE METHODS ----------

    def get_movies(self, user_id: int) -> list[Movie]:
        """Get all movies belonging to a specific user."""
        return Movie.query.filter_by(user_id=user_id).order_by(Movie.name).all()

    def add_movie(self, user_id: int, title: str) -> Movie | None:
        """
        Add a new movie for a user.
        Fetches details from the OMDb API if an API key is available.

        :param user_id: ID of the user who owns this movie.
        :param title: Movie title (used to query OMDb).
        :return: The created Movie object or None if OMDb lookup failed.
        """
        movie_data = self._fetch_omdb_data(title) if self.omdb_api_key else None

        new_movie = Movie(
            name=movie_data.get("Title") if movie_data else title,
            director=movie_data.get("Director") if movie_data else None,
            year=int(movie_data.get("Year")) if movie_data and movie_data.get("Year", "").isdigit() else None,
            poster_url=movie_data.get("Poster") if movie_data else None,
            user_id=user_id
        )

        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id: int, new_title: str = None, director: str = None, year: int = None) -> Movie | None:
        """Update the details of a specific movie."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return None

        if new_title:
            movie.name = new_title
        if director:
            movie.director = director
        if year:
            movie.year = year

        db.session.commit()
        return movie

    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie from the database."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie)
        db.session.commit()
        return True

    # ---------- OMDb HELPER METHOD ----------

    def _fetch_omdb_data(self, title: str) -> dict | None:
        """
        Fetch movie data from the OMDb API based on the movie title.
        :param title: The movie title to look up.
        :return: Dictionary with OMDb data or None if not found.
        """
        url = "https://www.omdbapi.com/"
        params = {"t": title, "apikey": self.omdb_api_key}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                return data
            return None
        except requests.RequestException:
            return None
