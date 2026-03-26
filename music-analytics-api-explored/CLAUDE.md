# Music Analytics API

A Flask-based REST API for music data analytics, providing endpoints for artists, albums, and statistics.

## Project Structure

- `app.py` - Flask application entry point
- `routes.py` - API endpoint definitions
- `models.py` - Artist and Album data models with in-memory store
- `analytics.py` - Statistical analysis functions
- `config.py` - Session and app configuration
- `middleware.py` - Request logging

## Running the App

```bash
flask run
# or
python app.py
```

## API Endpoints

- `GET /artists` - List all artists
- `GET /artists/<id>` - Get artist by ID
- `GET /artists/<id>/albums` - Get albums by artist
- `GET /albums` - List all albums
- `GET /stats/albums` - Album popularity statistics
- `GET /stats/average-tracks` - Average tracks per album

## Configuration

Uses filesystem-based sessions configured in `config.py`.

## Coding Conventions

- Use type hints for function parameters
- Include docstrings for all public functions
- Follow PEP 8 style guidelines
