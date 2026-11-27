"""API Routes for Music Analytics."""

from flask import jsonify, request, session
from app import app
from models import Album, music_store
from analytics import calculate_album_stats, calculate_average_tracks

POPULARITY_PER_TRACK = 5  # Simple popularity metric: each track adds 5 points


def prepare_album_stats_data(albums: list[Album]) -> list[dict]:
    """Convert albums into the dicts expected by calculate_album_stats.

    Args:
        albums: Album objects from the music store.

    Returns:
        One dict per album with album_id, title, track_count and a popularity
        score of track_count * POPULARITY_PER_TRACK.
    """
    return [
        {
            'album_id': a.album_id,
            'title': a.title,
            'track_count': a.track_count,
            'popularity': a.track_count * POPULARITY_PER_TRACK
        }
        for a in albums
    ]


def prepare_track_count_data(albums: list[Album]) -> list[dict]:
    """Convert albums into the dicts expected by calculate_average_tracks.

    Args:
        albums: Album objects from the music store.

    Returns:
        One dict per album containing only its track_count.
    """
    return [{'track_count': a.track_count} for a in albums]


@app.route('/artists', methods=['GET'])
def get_artists():
    """Return all artists."""
    artists = music_store.get_all_artists()
    return jsonify([a.to_dict() for a in artists])


@app.route('/artists/<int:artist_id>', methods=['GET'])
def get_artist(artist_id):
    """Return a single artist by ID."""
    artist = music_store.get_artist(artist_id)
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    return jsonify(artist.to_dict())


@app.route('/artists/<int:artist_id>/albums', methods=['GET'])
def get_artist_albums(artist_id):
    """Return all albums for an artist."""
    albums = music_store.get_albums_by_artist(artist_id)
    return jsonify([a.to_dict() for a in albums])


@app.route('/albums', methods=['GET'])
def get_albums():
    """Return all albums."""
    albums = music_store.get_all_albums()
    return jsonify([a.to_dict() for a in albums])


@app.route('/stats/albums', methods=['GET'])
def get_album_stats():
    """Return album statistics."""
    album_dicts = prepare_album_stats_data(music_store.get_all_albums())
    stats = calculate_album_stats(album_dicts)
    return jsonify(stats)


@app.route('/stats/average-tracks', methods=['GET'])
def get_average_tracks():
    """Return average tracks per album."""
    album_dicts = prepare_track_count_data(music_store.get_all_albums())
    avg = calculate_average_tracks(album_dicts)
    return jsonify({'average_tracks': avg})
