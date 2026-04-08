"""Test suite for Music Analytics Reporter."""

import csv
import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

import reporter


@pytest.fixture
def db_path(tmp_path):
    """Create a minimal seeded SQLite test database.

    Contains:
    - 1 artist (Test Artist)
    - 2 albums, 5 tracks across 2 genres (Rock, Metal)
    - Some invoice_items for revenue
    """
    db_file = tmp_path / "test.db"

    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA foreign_keys = ON")

    # Create schema
    conn.execute("""
        CREATE TABLE artists (
            ArtistId INTEGER PRIMARY KEY,
            Name TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE albums (
            AlbumId INTEGER PRIMARY KEY,
            Title TEXT NOT NULL,
            ArtistId INTEGER NOT NULL,
            FOREIGN KEY(ArtistId) REFERENCES artists(ArtistId)
        )
    """)

    conn.execute("""
        CREATE TABLE genres (
            GenreId INTEGER PRIMARY KEY,
            Name TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE tracks (
            TrackId INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            AlbumId INTEGER NOT NULL,
            GenreId INTEGER NOT NULL,
            Milliseconds INTEGER NOT NULL,
            FOREIGN KEY(AlbumId) REFERENCES albums(AlbumId),
            FOREIGN KEY(GenreId) REFERENCES genres(GenreId)
        )
    """)

    conn.execute("""
        CREATE TABLE invoice_items (
            InvoiceLineId INTEGER PRIMARY KEY,
            TrackId INTEGER NOT NULL,
            UnitPrice REAL NOT NULL,
            Quantity INTEGER NOT NULL,
            FOREIGN KEY(TrackId) REFERENCES tracks(TrackId)
        )
    """)

    # Insert test data
    conn.execute("INSERT INTO artists VALUES (1, 'Test Artist')")

    conn.execute("INSERT INTO albums VALUES (1, 'Album A', 1)")
    conn.execute("INSERT INTO albums VALUES (2, 'Album B', 1)")

    conn.execute("INSERT INTO genres VALUES (1, 'Rock')")
    conn.execute("INSERT INTO genres VALUES (2, 'Metal')")

    # Album A: 3 tracks (2 Rock, 1 Metal)
    conn.execute("INSERT INTO tracks VALUES (1, 'Track 1', 1, 1, 180000)")
    conn.execute("INSERT INTO tracks VALUES (2, 'Track 2', 1, 1, 200000)")
    conn.execute("INSERT INTO tracks VALUES (3, 'Track 3', 1, 2, 150000)")

    # Album B: 2 tracks (1 Rock, 1 Metal)
    conn.execute("INSERT INTO tracks VALUES (4, 'Track 4', 2, 1, 200000)")
    conn.execute("INSERT INTO tracks VALUES (5, 'Track 5', 2, 2, 180000)")

    # Add some invoice items (revenue)
    conn.execute("INSERT INTO invoice_items VALUES (1, 1, 0.99, 2)")
    conn.execute("INSERT INTO invoice_items VALUES (2, 2, 0.99, 1)")
    conn.execute("INSERT INTO invoice_items VALUES (3, 3, 0.99, 0)")  # Zero quantity
    conn.execute("INSERT INTO invoice_items VALUES (4, 4, 0.99, 3)")
    # Track 5 has no invoice items (zero revenue)

    conn.commit()
    conn.close()

    return str(db_file)


class TestGetDbConnection:
    """Tests for get_db_connection()."""

    def test_success(self, db_path):
        """Test successful database connection."""
        conn = reporter.get_db_connection(db_path)
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_missing_file(self):
        """Test error when database file does not exist."""
        with pytest.raises(SystemExit):
            reporter.get_db_connection("/nonexistent/path/to/db.db")

    def test_invalid_file(self, tmp_path):
        """Test error when file is not a valid SQLite database."""
        invalid_db = tmp_path / "invalid.db"
        invalid_db.write_text("not a valid sqlite database")

        with pytest.raises(SystemExit):
            reporter.get_db_connection(str(invalid_db))


class TestFetchArtistStats:
    """Tests for fetch_artist_stats()."""

    def test_known_artist(self, db_path):
        """Test fetching stats for an artist in the database."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        assert data is not None
        assert data["artist"] == "Test Artist"
        assert data["album_count"] == 2
        assert data["track_count"] == 5
        assert len(data["albums"]) == 2

    def test_unknown_artist(self, db_path):
        """Test fetching stats for non-existent artist."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Unknown Artist")
        conn.close()

        assert data is None

    def test_multi_genre(self, db_path):
        """Test that genres are correctly aggregated."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        assert "Metal" in data["genres"]
        assert "Rock" in data["genres"]
        assert len(data["genres"]) == 2

    def test_albums_sorted(self, db_path):
        """Test that albums are sorted by title."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        album_titles = [album["album_title"] for album in data["albums"]]
        assert album_titles == sorted(album_titles)

    def test_revenue_calculation(self, db_path):
        """Test that revenue is calculated correctly."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        # Track 1: 0.99 * 2 = 1.98
        # Track 2: 0.99 * 1 = 0.99
        # Track 3: 0.99 * 0 = 0.0
        # Total for Album A: 2.97
        assert data["albums"][0]["revenue"] == 2.97

        # Track 4: 0.99 * 3 = 2.97
        # Track 5: no invoice items = 0.0
        # Total for Album B: 2.97
        assert data["albums"][1]["revenue"] == 2.97

        # Total: 5.94
        assert data["total_revenue"] == 5.94


class TestFormatJson:
    """Tests for format_json()."""

    def test_round_trip(self, db_path):
        """Test that JSON output can be parsed back."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        json_str = reporter.format_json(data)
        parsed = json.loads(json_str)

        assert parsed["artist"] == data["artist"]
        assert parsed["album_count"] == data["album_count"]

    def test_genres_is_list(self, db_path):
        """Test that genres are formatted as a list in JSON."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        json_str = reporter.format_json(data)
        parsed = json.loads(json_str)

        assert isinstance(parsed["genres"], list)
        assert len(parsed["genres"]) == 2

    def test_albums_nested(self, db_path):
        """Test that albums are nested correctly in JSON."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        json_str = reporter.format_json(data)
        parsed = json.loads(json_str)

        assert isinstance(parsed["albums"], list)
        assert len(parsed["albums"]) == 2
        assert "album_title" in parsed["albums"][0]


class TestFormatCsv:
    """Tests for format_csv()."""

    def test_two_sections_with_separator(self, db_path):
        """Test that CSV has two sections with blank line separator."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        csv_str = reporter.format_csv(data)
        lines = csv_str.split("\n")

        # Find blank line (should separate artist summary from albums)
        blank_line_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "":
                blank_line_idx = i
                break

        assert blank_line_idx is not None
        # Blank line should be around line 2 (after header and data row)
        assert 2 <= blank_line_idx <= 3

    def test_summary_values(self, db_path):
        """Test that artist summary row contains correct values."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        csv_str = reporter.format_csv(data)
        lines = csv_str.split("\n")

        # Second line should be the artist summary
        reader = csv.reader(io.StringIO(lines[1]))
        row = next(reader)

        assert row[0] == "Test Artist"
        assert row[1] == "2"  # album_count
        assert row[2] == "5"  # track_count

    def test_pipe_delimited_genres(self, db_path):
        """Test that multiple genres are pipe-delimited."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        csv_str = reporter.format_csv(data)
        lines = csv_str.split("\n")

        # Second line should be the artist summary
        reader = csv.reader(io.StringIO(lines[1]))
        row = next(reader)

        genres_cell = row[5]
        assert "|" in genres_cell
        assert "Rock" in genres_cell
        assert "Metal" in genres_cell

    def test_correct_album_row_count(self, db_path):
        """Test that CSV has correct number of album rows."""
        conn = reporter.get_db_connection(db_path)
        data = reporter.fetch_artist_stats(conn, "Test Artist")
        conn.close()

        csv_str = reporter.format_csv(data)
        lines = csv_str.split("\n")

        # Find blank line
        blank_line_idx = None
        for i, line in enumerate(lines):
            if line.strip() == "":
                blank_line_idx = i
                break

        # After blank line: header + 2 albums + blank at end
        album_lines = lines[blank_line_idx + 2:]
        non_empty_lines = [l for l in album_lines if l.strip()]

        assert len(non_empty_lines) == 2  # Header + 2 albums


class TestWriteOutput:
    """Tests for write_output()."""

    def test_creates_file(self, tmp_path):
        """Test that output file is created."""
        output_path = tmp_path / "output.txt"
        content = "Test content"

        reporter.write_output(content, str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == content

    def test_unwritable_path(self, tmp_path):
        """Test error when output path is not writable."""
        # Create a directory where we expect a file
        unwritable_dir = tmp_path / "subdir"
        unwritable_dir.mkdir()
        output_path = unwritable_dir / "file" / "output.txt"

        with pytest.raises(SystemExit):
            reporter.write_output("content", str(output_path))


class TestMain:
    """Integration tests for main()."""

    def test_json_output_valid(self, db_path, tmp_path, monkeypatch):
        """Test that main() produces valid JSON output."""
        output_file = tmp_path / "output.json"

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "reporter.py",
                "--artist",
                "Test Artist",
                "--format",
                "json",
                "--output",
                str(output_file),
                "--db",
                db_path,
            ],
        )

        reporter.main()

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["artist"] == "Test Artist"
        assert data["album_count"] == 2

    def test_csv_headers_present(self, db_path, tmp_path, monkeypatch):
        """Test that main() produces CSV with correct headers."""
        output_file = tmp_path / "output.csv"

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "reporter.py",
                "--artist",
                "Test Artist",
                "--format",
                "csv",
                "--output",
                str(output_file),
                "--db",
                db_path,
            ],
        )

        reporter.main()

        assert output_file.exists()
        lines = output_file.read_text().split("\n")
        assert "artist,album_count,track_count" in lines[0]

    def test_artist_not_found_exits(self, db_path, monkeypatch, capsys):
        """Test that main() exits with error for unknown artist."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "reporter.py",
                "--artist",
                "Unknown",
                "--format",
                "json",
                "--output",
                "/tmp/out.json",
                "--db",
                db_path,
            ],
        )

        with pytest.raises(SystemExit):
            reporter.main()

    def test_db_not_found_exits(self, monkeypatch, capsys):
        """Test that main() exits with error for missing database."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "reporter.py",
                "--artist",
                "Test Artist",
                "--format",
                "json",
                "--output",
                "/tmp/out.json",
                "--db",
                "/nonexistent/db.db",
            ],
        )

        with pytest.raises(SystemExit):
            reporter.main()
