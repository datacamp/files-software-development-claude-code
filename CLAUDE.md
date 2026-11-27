# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Course material for DataCamp's "Software Development with Claude Code". It is not one application: each top-level `music-analytics-*` folder is a **self-contained snapshot of the same small project at a different exercise stage**. Work inside one folder at a time, and do not "fix" a folder to match another one, because the differences between them (including planted bugs) are the point of the exercises.

Most exercise folders have their own `CLAUDE.md` (and some have `.claude/` agents, skills and settings) describing the task for that stage. When working in a folder, follow its `CLAUDE.md`; it takes precedence over this file. Some of them impose hard rules, e.g. `music-analytics-reporter-plan/CLAUDE.md` says to produce a plan only and write no code.

## Environment and commands

Dependencies are declared once at the repo root (`pyproject.toml`, `uv.lock`, Python 3.12). There is no per-folder dependency file, no linter config and no build step.

```bash
uv sync                      # install deps into .venv at the repo root
```

Modules import each other by bare name (`from app import app`, `import reporter`), so **run everything from inside the exercise folder**:

```bash
cd music-analytics-api-refactor
uv run --project .. python -m pytest                            # whole suite
uv run --project .. python -m pytest test_routes.py::TestGetArtists          # one class
uv run --project .. python -m pytest "test_routes.py::TestGetArtists::test_get_artists_success"  # one test
uv run --project .. flask run                                   # or: python3 app.py
```

If the root `.venv` is activated, plain `python3 -m pytest` works too (the per-folder `CLAUDE.md` files use that form and ask for `python3`).

Reporter CLI (in folders that contain `reporter.py`):

```bash
python3 reporter.py --artist "AC/DC" --format json --output report.json [--db chinook.db]
```

## Architecture of the Music Analytics API folders

All `music-analytics-api*` folders share one Flask layout:

- `app.py` creates the `Flask` app, configures Flask-Session from `config.Config` (cachelib filesystem sessions under `/tmp/flask_session`), then does `from routes import *` **at the bottom of the file**. `routes.py` in turn does `from app import app` and registers its routes with `@app.route`. This circular import is intentional; new route modules must be imported after `app` is created, or the import will fail.
- `models.py` holds `Artist`/`Album` classes and a module-level `music_store` singleton (`MusicStore`), an in-memory mock loaded with 5 artists and 8 albums. It is not backed by the database.
- `analytics.py` has pure functions over lists of dicts (`calculate_album_stats`, `calculate_average_tracks`), called from the `/stats/*` routes. `routes.py` converts model objects to dicts before calling them (`/stats/albums` derives `popularity = track_count * 5`).
- `middleware.py` defines request-timing hooks, but nothing imports it, so they are not active unless an exercise wires them in.
- `test_routes.py` (where present) uses Flask's test client and patches `routes.music_store` with mocks, so these tests do not touch `chinook.db`.

The `-with-db*` stages add the Chinook database:

- `db_routes.py` defines a Blueprint `db_bp` that queries the folder's own `chinook.db` with raw `sqlite3` (tables `Artist`, `Album`, … in PascalCase). It is registered in `app.py` **before** `from routes import *`, so its `/artists/<id>/albums` takes precedence over the in-memory route of the same path. Because of this, the mock-based `TestGetArtistAlbums` tests fail in `-with-db-routed` and `-with-db-routed-validated`.
- `-with-db-routed-validated` adds Pydantic response models (`AlbumResponse`, `AlbumsListResponse`) in `models.py`, serialised with `model_dump(by_alias=True)`.

## Reporter folders

`music-analytics-reporter-{plan,build,test,review}` are stages of one CLI tool (`reporter.py`) that builds an artist report from Chinook with raw `sqlite3` (no ORM). `PLAN.md` holds the plan produced in the plan stage, and `build` has only the plan, no code yet. `test_reporter.py` seeds its own temporary SQLite database in a fixture rather than using `chinook.db`.

## Database

`chinook.db` is the Chinook sample music-store database (SQLite). There is one at the root and copies inside the folders that use it; code resolves the path relative to its own folder. `MCP/` shows how to expose it to Claude Code through `uvx mcp-server-sqlite`.

## Hooks

`Hooks/` and several folders' `.claude/settings.json` define a `PostToolUse` hook that runs pytest after every `Write`/`Edit`. The per-folder hooks run `python -m pytest tests/`, but tests sit at the folder root (`test_routes.py`), not in `tests/`, so that hook command finds no tests as written. `Hooks/conftest.py` (copied into `-with-hooks`) logs results to `/tmp/pytest_results.log` and sends a desktop notification.
