# Music Analytics Reporter

A CLI tool for generating reports from the Chinook music database.

## Project Structure

- `reporter.py` - Main CLI tool (creates artist statistics reports)
- `chinook.db` - SQLite database with music catalog data
- `test_reporter.py` - Test suite using pytest

## Database

The Chinook database contains artists, albums, tracks, genres, and invoice data.
Use MCP to query the database directly.

## CLI Usage

```bash
python reporter.py --artist "AC/DC" --format json --output report.json
python reporter.py --artist "Aerosmith" --format csv --output report.csv
```
