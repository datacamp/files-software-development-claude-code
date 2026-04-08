# Music Analytics Reporter

A CLI tool for generating reports from the Chinook music database.

## Project Structure

- `reporter.py` - Main CLI tool (creates artist statistics reports)
- `chinook.db` - SQLite database with music catalog data
- `test_reporter.py` - Test suite using pytest

## Database

The Chinook database contains artists, albums, tracks, genres, and invoice data.
Use MCP to query the database directly.

## CLI Requirements

- `--artist` (required): artist name, case-insensitive
- `--format` (required): `json` or `csv`
- `--output` (required): output file path
- `--db` (optional): database path, defaults to `chinook.db`

Report must include album/track counts, genres, total revenue, and per-album breakdown.
Use `sqlite3` directly — no ORM.

## Important

Do not write any code or create any files. Produce a plan only.

## CLI Usage

```bash
python3 reporter.py --artist "AC/DC" --format json --output report.json
python3 reporter.py --artist "Aerosmith" --format csv --output report.csv
```

## Running tests

```bash
python3 -m pytest
```
