# 🎬 MovieWebApp

MovieWebApp is a simple Flask web application that lets users manage their favorite movies.  
Movie data (title, year, director, and poster) is automatically fetched from the **OMDb API**.

---

## 🚀 Features

- Create and manage users  
- Add and remove movies for each user  
- Automatically fetch movie details and posters from the OMDb API  
- Responsive front-end with Flask, HTML, and CSS  
- Custom **error handling** for HTTP and server exceptions  
- Logging for unexpected errors  

---

## 🧰 Tech Stack

| Komponente | Beschreibung |
|-------------|--------------|
| **Backend** | Flask (Python 3.12) |
| **Frontend** | HTML, Jinja2, CSS |
| **Database** | SQLite (SQLAlchemy ORM) |
| **API** | OMDb API (Open Movie Database) |
| **Env Management** | python-dotenv |
| **Logging** | Python logging-Modul |

---

##  Setup

## 1. clone repository 
```bash
git clone https://github.com/<your-username>/MoviWebApp.git
cd MoviWebApp
```
## Activate viritual enviroment
python3 -m venv .venv
source .venv/bin/activate     # macOS/Linux
# or
.venv\Scripts\activate        # Windows

## 2. install requirements
pip install -r requirements.txt

## 3. create .env
FLASK_SECRET_KEY=your_secret_key
OMDB_API_KEY=your_omdb_api_key

## 📦 Installation
pip install -r requirements.txt


