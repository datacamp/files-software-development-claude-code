# Plan: Music Analytics Reporter CLI

## Context

The project scaffolding exists (chinook.db, pyproject.toml) but `reporter.py` and `test_reporter.py` have not been created yet. This plan describes how to build a CLI tool that queries the Chinook SQLite database for per-artist statistics and exports to JSON or CSV, using Python stdlib only (no new dependencies).

---

## Files to Create

- `reporter.py` (~160 lines)
- `test_reporter.py` (~220 lines)

---

## Module Structure: `reporter.py`

Five layers with single responsibilities:

```
get_db_connection(db_path)           -> sqlite3.Connection
fetch_artist_stats(conn, name)       -> dict | None
format_json(data)                    -> str
format_csv(data)                     -> str
write_output(content, output_path)   -> None
parse_args()                         -> argparse.Namespace
main()
```

### Key design decisions

- `sqlite3.Row` for named column access
- Open DB in read-only URI mode: `file:chinook.db?mode=ro`
- `--db` optional flag (default `chinook.db`) allows tests to inject a temp DB path
- Artist lookup uses `LIKE` (case-insensitive for ASCII); `=` fails for lowercase "ac/dc"

---

## SQL Queries (inside `fetch_artist_stats`)

**1. Top-level aggregates**
```sql
SELECT ar.ArtistId, ar.Name,
       COUNT(DISTINCT al.AlbumId) AS album_count,
       COUNT(t.TrackId)           AS track_count,
       ROUND(SUM(t.Milliseconds) / 1000.0, 3) AS total_duration_seconds
FROM artists ar
LEFT JOIN albums al ON al.ArtistId = ar.ArtistId
LEFT JOIN tracks  t  ON t.AlbumId  = al.AlbumId
WHERE ar.Name LIKE ?
GROUP BY ar.ArtistId, ar.Name
```

**2. Per-album breakdown**
```sql
SELECT al.AlbumId, al.Title AS album_title,
       COUNT(t.TrackId) AS track_count,
       ROUND(SUM(t.Milliseconds) / 1000.0, 3) AS duration_seconds,
       ROUND(SUM(ii.UnitPrice * ii.Quantity), 2) AS revenue
FROM albums al
JOIN tracks t ON t.AlbumId = al.AlbumId
LEFT JOIN invoice_items ii ON ii.TrackId = t.TrackId
WHERE al.ArtistId = ?
GROUP BY al.AlbumId, al.Title
ORDER BY al.Title
```

**3. Distinct genres**
```sql
SELECT DISTINCT g.Name AS genre_name
FROM albums al
JOIN tracks t ON t.AlbumId = al.AlbumId
JOIN genres g ON g.GenreId = t.GenreId
WHERE al.ArtistId = ?
ORDER BY g.Name
```

**4. Total revenue (scalar)**
```sql
SELECT ROUND(SUM(ii.UnitPrice * ii.Quantity), 2) AS total_revenue
FROM albums al
JOIN tracks t ON t.AlbumId = al.AlbumId
JOIN invoice_items ii ON ii.TrackId = t.TrackId
WHERE al.ArtistId = ?
```
Coerce NULL → `0.0` in Python: `row["total_revenue"] or 0.0`

---

## Output Data Structure

```python
{
    "artist": "AC/DC",
    "album_count": 2,
    "track_count": 18,
    "total_duration_seconds": 4853.674,
    "total_revenue": 15.84,
    "genres": ["Rock"],
    "albums": [
        {"album_title": "...", "track_count": 10,
         "duration_seconds": 2400.415, "revenue": 9.9},
        ...
    ]
}
```

### JSON: `json.dumps(data, indent=2)`

### CSV: Two sections separated by a blank line
```
artist,album_count,track_count,total_duration_seconds,total_revenue,genres
AC/DC,2,18,4853.674,15.84,Rock

album_title,track_count,duration_seconds,revenue
For Those About To Rock We Salute You,10,2400.415,9.9
Let There Be Rock,8,2453.259,5.94
```
Multi-genre artists: pipe-delimited in genres cell (`Rock|Metal`).
Built via `csv.writer` on an `io.StringIO` buffer.

---

## CLI Arguments

| Flag | Required | Default | Notes |
|------|----------|---------|-------|
| `--artist` | yes | — | case-insensitive lookup |
| `--format` | yes | — | `json` or `csv` |
| `--output` | yes | — | output file path |
| `--db` | no | `chinook.db` | test injection |

---

## Error Handling

| Condition | Response |
|-----------|----------|
| DB file not found | `sys.exit("Error: Database not found: ...")` |
| File not valid SQLite | `sys.exit("Error: database file is invalid: ...")` |
| Artist not found | `sys.exit("Error: artist 'X' not found in database.")` |
| Output not writable | `sys.exit("Error: could not write output file: ...")` |

---

## Test Suite: `test_reporter.py`

**Fixture**: `db_path(tmp_path)` — creates a minimal seeded SQLite DB with:
- 1 artist (`Test Artist`)
- 2 albums, 5 tracks across 2 genres (Rock, Metal)
- Some invoice_items for revenue

**Test coverage:**

| Function | Tests |
|----------|-------|
| `get_db_connection` | success, missing file, invalid file |
| `fetch_artist_stats` | known artist, unknown artist, case-insensitive, zero sales, multi-genre, albums sorted |
| `format_json` | round-trips via `json.loads`, genres is list, albums nested |
| `format_csv` | two sections with blank separator, summary values, pipe-delimited genres, correct album row count |
| `write_output` | creates file, unwritable path raises OSError |
| `main` (integration) | JSON output valid, CSV headers present, artist-not-found exits, db-not-found exits |

Tests use `monkeypatch.setattr(sys, 'argv', [...])` and `pytest.raises(SystemExit)` + `capsys` for CLI integration tests.

---

## Verification

```bash
# Run against live DB
python reporter.py --artist "AC/DC" --format json --output /tmp/acdc.json
python reporter.py --artist "Aerosmith" --format csv --output /tmp/aero.csv

# Run test suite
pytest test_reporter.py -v
```

Expected: AC/DC returns 2 albums, 18 tracks, genre Rock, ~15.84 revenue.
