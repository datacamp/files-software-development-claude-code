#!/usr/bin/env python3
"""Music Analytics Reporter - Query Chinook DB for per-artist statistics."""

import argparse
import csv
import io
import json
import sqlite3
import sys
from pathlib import Path


def get_db_connection(db_path):
    """Open a read-only connection to the SQLite database.

    Args:
        db_path: Path to the database file

    Returns:
        sqlite3.Connection in read-only URI mode

    Raises:
        FileNotFoundError: If database file does not exist
        sqlite3.DatabaseError: If file is not a valid SQLite database
    """
    path = Path(db_path)
    if not path.exists():
        sys.exit(f"Error: Database not found: {db_path}")

    try:
        uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        # Test the connection by running a simple query
        conn.execute("SELECT 1").fetchone()
        return conn
    except sqlite3.DatabaseError as e:
        sys.exit(f"Error: database file is invalid: {db_path}")


def fetch_artist_stats(conn, artist_name):
    """Fetch aggregated stats for an artist.

    Args:
        conn: sqlite3.Connection
        artist_name: Name of the artist to query

    Returns:
        dict with artist stats or None if not found
    """
    # Query 1: Top-level aggregates
    query1 = """
        SELECT ar.ArtistId, ar.Name,
               COUNT(DISTINCT al.AlbumId) AS album_count,
               COUNT(t.TrackId) AS track_count,
               ROUND(SUM(t.Milliseconds) / 1000.0, 3) AS total_duration_seconds
        FROM artists ar
        LEFT JOIN albums al ON al.ArtistId = ar.ArtistId
        LEFT JOIN tracks t ON t.AlbumId = al.AlbumId
        WHERE ar.Name LIKE ?
        GROUP BY ar.ArtistId, ar.Name
    """

    cursor = conn.execute(query1, (artist_name,))
    top_row = cursor.fetchone()

    if not top_row:
        return None

    artist_id = top_row["ArtistId"]

    # Query 2: Per-album breakdown
    query2 = """
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
    """

    cursor = conn.execute(query2, (artist_id,))
    albums = [dict(row) for row in cursor.fetchall()]

    # Coerce NULL revenue to 0.0
    for album in albums:
        if album["revenue"] is None:
            album["revenue"] = 0.0

    # Query 3: Distinct genres
    query3 = """
        SELECT DISTINCT g.Name AS genre_name
        FROM albums al
        JOIN tracks t ON t.AlbumId = al.AlbumId
        JOIN genres g ON g.GenreId = t.GenreId
        WHERE al.ArtistId = ?
        ORDER BY g.Name
    """

    cursor = conn.execute(query3, (artist_id,))
    genres = [row["genre_name"] for row in cursor.fetchall()]

    # Query 4: Total revenue (scalar)
    query4 = """
        SELECT ROUND(SUM(ii.UnitPrice * ii.Quantity), 2) AS total_revenue
        FROM albums al
        JOIN tracks t ON t.AlbumId = al.AlbumId
        JOIN invoice_items ii ON ii.TrackId = t.TrackId
        WHERE al.ArtistId = ?
    """

    cursor = conn.execute(query4, (artist_id,))
    revenue_row = cursor.fetchone()
    total_revenue = revenue_row["total_revenue"] or 0.0

    return {
        "artist": top_row["Name"],
        "album_count": top_row["album_count"],
        "track_count": top_row["track_count"],
        "total_duration_seconds": top_row["total_duration_seconds"],
        "total_revenue": total_revenue,
        "genres": genres,
        "albums": albums,
    }


def format_json(data):
    """Format artist stats as JSON.

    Args:
        data: dict with artist stats

    Returns:
        JSON string with indent=2
    """
    return json.dumps(data, indent=2)


def format_csv(data):
    """Format artist stats as CSV with two sections.

    Args:
        data: dict with artist stats

    Returns:
        CSV string with artist summary and albums breakdown
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Section 1: Artist summary
    genres_str = "|".join(data["genres"])
    writer.writerow([
        "artist",
        "album_count",
        "track_count",
        "total_duration_seconds",
        "total_revenue",
        "genres",
    ])
    writer.writerow([
        data["artist"],
        data["album_count"],
        data["track_count"],
        data["total_duration_seconds"],
        data["total_revenue"],
        genres_str,
    ])

    # Blank line separator
    buffer.write("\n")

    # Section 2: Album breakdown
    writer.writerow([
        "album_title",
        "track_count",
        "duration_seconds",
        "revenue",
    ])
    for album in data["albums"]:
        writer.writerow([
            album["album_title"],
            album["track_count"],
            album["duration_seconds"],
            album["revenue"],
        ])

    return buffer.getvalue()


def write_output(content, output_path):
    """Write content to output file.

    Args:
        content: String content to write
        output_path: Path to output file

    Raises:
        SystemExit: If file cannot be written
    """
    try:
        Path(output_path).write_text(content)
    except OSError as e:
        sys.exit(f"Error: could not write output file: {output_path}")


def parse_args():
    """Parse command-line arguments.

    Returns:
        argparse.Namespace with artist, format, output, and db
    """
    parser = argparse.ArgumentParser(
        description="Generate reports from the Chinook music database"
    )
    parser.add_argument(
        "--artist",
        required=True,
        help="Artist name to query (case-insensitive)",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=["json", "csv"],
        help="Output format",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path",
    )
    parser.add_argument(
        "--db",
        default="chinook.db",
        help="Database file path (default: chinook.db)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Connect to database
    conn = get_db_connection(args.db)

    # Fetch artist stats
    data = fetch_artist_stats(conn, args.artist)
    if data is None:
        sys.exit(f"Error: artist '{args.artist}' not found in database.")

    # Format output
    if args.format == "json":
        content = format_json(data)
    else:  # csv
        content = format_csv(data)

    # Write output
    write_output(content, args.output)

    conn.close()


if __name__ == "__main__":
    main()
