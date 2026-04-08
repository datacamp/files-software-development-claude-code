# Music Analytics API

A Flask-based REST API for music data analytics.

## Project state

The API currently serves data from an in-memory mock store (`routes.py` and `models.py`).
The Chinook SQLite database (`chinook.db`) is in this directory and connected via MCP.

## Your task

Create a new `db_routes.py` Flask Blueprint with an endpoint at `/artists/<artist_id>/albums`
that queries `chinook.db` using `sqlite3`. Register the Blueprint with `app.py`.

## Running tests

```bash
python3 -m pytest
```

## Hooks

This project has a PostToolUse hook configured that automatically runs tests after any file edit.

## Coding conventions

- Use `python3` for all Python commands
- Use type hints for function parameters
- Include docstrings for all public functions
- Follow PEP 8 style guidelines