"""Database routes for Chinook using SQLite."""

import sqlite3
from flask import Blueprint, jsonify
from pathlib import Path
from models import AlbumsListResponse, AlbumResponse

db_bp = Blueprint('db', __name__)

# Path to Chinook database
DB_PATH = Path(__file__).parent / 'chinook.db'


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


@db_bp.route('/artists/<int:artist_id>/albums', methods=['GET'])
def get_artist_albums(artist_id: int):
    """Return all albums for a specific artist from Chinook database.

    Args:
        artist_id: The ID of the artist

    Returns:
        JSON array of albums for the artist
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify artist exists
        cursor.execute('SELECT ArtistId, Name FROM Artist WHERE ArtistId = ?', (artist_id,))
        artist = cursor.fetchone()

        if not artist:
            conn.close()
            return jsonify({'error': 'Artist not found'}), 404

        # Get all albums for the artist
        cursor.execute(
            'SELECT AlbumId, Title, ArtistId FROM Album WHERE ArtistId = ? ORDER BY Title',
            (artist_id,)
        )
        albums = cursor.fetchall()
        conn.close()

        # Return 404 if artist has no albums
        if not albums:
            return jsonify({'error': 'Artist has no albums'}), 404

        # Convert to Pydantic models and validate
        album_responses = [
            AlbumResponse(
                AlbumId=album['AlbumId'],
                title=album['Title'],
                ArtistId=album['ArtistId']
            )
            for album in albums
        ]

        # Create and validate the response
        response = AlbumsListResponse(
            albums=album_responses,
            artist_id=artist_id,
            album_count=len(albums)
        )

        return jsonify(response.model_dump(by_alias=True))

    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
