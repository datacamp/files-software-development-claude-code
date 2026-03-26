"""Unit tests for Music Analytics API routes."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app import app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class MockArtist:
    """Mock Artist object for testing."""

    def __init__(self, artist_id, name):
        self.artist_id = artist_id
        self.name = name

    def to_dict(self):
        return {'artist_id': self.artist_id, 'name': self.name}


class MockAlbum:
    """Mock Album object for testing."""

    def __init__(self, album_id, title, artist_id, track_count):
        self.album_id = album_id
        self.title = title
        self.artist_id = artist_id
        self.track_count = track_count

    def to_dict(self):
        return {
            'album_id': self.album_id,
            'title': self.title,
            'artist_id': self.artist_id,
            'track_count': self.track_count
        }


class TestGetArtists:
    """Tests for GET /artists endpoint."""

    @patch('routes.music_store')
    def test_get_artists_success(self, mock_store, client):
        """Test retrieving all artists successfully."""
        mock_artists = [
            MockArtist(1, 'Artist 1'),
            MockArtist(2, 'Artist 2')
        ]
        mock_store.get_all_artists.return_value = mock_artists

        response = client.get('/artists')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['artist_id'] == 1
        assert data[0]['name'] == 'Artist 1'
        assert data[1]['artist_id'] == 2
        assert data[1]['name'] == 'Artist 2'

    @patch('routes.music_store')
    def test_get_artists_empty(self, mock_store, client):
        """Test retrieving artists when none exist."""
        mock_store.get_all_artists.return_value = []

        response = client.get('/artists')

        assert response.status_code == 200
        data = response.get_json()
        assert data == []


class TestGetArtist:
    """Tests for GET /artists/<artist_id> endpoint."""

    @patch('routes.music_store')
    def test_get_artist_success(self, mock_store, client):
        """Test retrieving a single artist by ID."""
        mock_artist = MockArtist(1, 'Artist 1')
        mock_store.get_artist.return_value = mock_artist

        response = client.get('/artists/1')

        assert response.status_code == 200
        data = response.get_json()
        assert data['artist_id'] == 1
        assert data['name'] == 'Artist 1'

    @patch('routes.music_store')
    def test_get_artist_not_found(self, mock_store, client):
        """Test retrieving a non-existent artist."""
        mock_store.get_artist.return_value = None

        response = client.get('/artists/999')

        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Artist not found'

    def test_get_artist_invalid_id(self, client):
        """Test retrieving artist with invalid ID format."""
        response = client.get('/artists/invalid')

        assert response.status_code == 404


class TestGetArtistAlbums:
    """Tests for GET /artists/<artist_id>/albums endpoint."""

    @patch('routes.music_store')
    def test_get_artist_albums_success(self, mock_store, client):
        """Test retrieving albums for an artist."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
            MockAlbum(2, 'Album 2', 1, 12)
        ]
        mock_store.get_albums_by_artist.return_value = mock_albums

        response = client.get('/artists/1/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['album_id'] == 1
        assert data[0]['title'] == 'Album 1'
        assert data[1]['album_id'] == 2
        assert data[1]['title'] == 'Album 2'

    @patch('routes.music_store')
    def test_get_artist_albums_empty(self, mock_store, client):
        """Test retrieving albums when artist has none."""
        mock_store.get_albums_by_artist.return_value = []

        response = client.get('/artists/1/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_get_artist_albums_invalid_id(self, client):
        """Test retrieving albums with invalid artist ID."""
        response = client.get('/artists/invalid/albums')

        assert response.status_code == 404


class TestGetAlbums:
    """Tests for GET /albums endpoint."""

    @patch('routes.music_store')
    def test_get_albums_success(self, mock_store, client):
        """Test retrieving all albums."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
            MockAlbum(2, 'Album 2', 1, 12),
            MockAlbum(3, 'Album 3', 2, 15)
        ]
        mock_store.get_all_albums.return_value = mock_albums

        response = client.get('/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
        assert data[0]['album_id'] == 1
        assert data[2]['album_id'] == 3

    @patch('routes.music_store')
    def test_get_albums_empty(self, mock_store, client):
        """Test retrieving albums when none exist."""
        mock_store.get_all_albums.return_value = []

        response = client.get('/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert data == []


class TestGetAlbumStats:
    """Tests for GET /stats/albums endpoint."""

    @patch('routes.calculate_album_stats')
    @patch('routes.music_store')
    def test_get_album_stats_success(self, mock_store, mock_calc, client):
        """Test retrieving album statistics."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
            MockAlbum(2, 'Album 2', 1, 20)
        ]
        mock_store.get_all_albums.return_value = mock_albums

        mock_stats = {
            'total_albums': 2,
            'avg_popularity': 75,
            'max_popularity': 100
        }
        mock_calc.return_value = mock_stats

        response = client.get('/stats/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert data['total_albums'] == 2
        assert data['avg_popularity'] == 75
        assert data['max_popularity'] == 100

    @patch('routes.calculate_album_stats')
    @patch('routes.music_store')
    def test_get_album_stats_empty(self, mock_store, mock_calc, client):
        """Test album statistics with no albums."""
        mock_store.get_all_albums.return_value = []
        mock_calc.return_value = {'total_albums': 0, 'avg_popularity': 0}

        response = client.get('/stats/albums')

        assert response.status_code == 200
        data = response.get_json()
        assert data['total_albums'] == 0

    @patch('routes.calculate_album_stats')
    @patch('routes.music_store')
    def test_get_album_stats_popularity_calculation(self, mock_store, mock_calc, client):
        """Test that popularity is calculated correctly (track_count * 5)."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
        ]
        mock_store.get_all_albums.return_value = mock_albums
        mock_calc.return_value = {}

        response = client.get('/stats/albums')

        # Verify the stats function was called with correct data
        call_args = mock_calc.call_args[0][0]
        assert call_args[0]['album_id'] == 1
        assert call_args[0]['popularity'] == 50  # 10 * 5


class TestGetAverageTracks:
    """Tests for GET /stats/average-tracks endpoint."""

    @patch('routes.calculate_average_tracks')
    @patch('routes.music_store')
    def test_get_average_tracks_success(self, mock_store, mock_calc, client):
        """Test retrieving average tracks per album."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
            MockAlbum(2, 'Album 2', 1, 20),
            MockAlbum(3, 'Album 3', 2, 15)
        ]
        mock_store.get_all_albums.return_value = mock_albums
        mock_calc.return_value = 15.0

        response = client.get('/stats/average-tracks')

        assert response.status_code == 200
        data = response.get_json()
        assert data['average_tracks'] == 15.0

    @patch('routes.calculate_average_tracks')
    @patch('routes.music_store')
    def test_get_average_tracks_empty(self, mock_store, mock_calc, client):
        """Test average tracks when no albums exist."""
        mock_store.get_all_albums.return_value = []
        mock_calc.return_value = 0

        response = client.get('/stats/average-tracks')

        assert response.status_code == 200
        data = response.get_json()
        assert data['average_tracks'] == 0

    @patch('routes.calculate_average_tracks')
    @patch('routes.music_store')
    def test_get_average_tracks_single_album(self, mock_store, mock_calc, client):
        """Test average tracks with single album."""
        mock_albums = [MockAlbum(1, 'Album 1', 1, 12)]
        mock_store.get_all_albums.return_value = mock_albums
        mock_calc.return_value = 12

        response = client.get('/stats/average-tracks')

        assert response.status_code == 200
        data = response.get_json()
        assert data['average_tracks'] == 12

    @patch('routes.calculate_average_tracks')
    @patch('routes.music_store')
    def test_get_average_tracks_data_structure(self, mock_store, mock_calc, client):
        """Test that track counts are passed correctly to analytics function."""
        mock_albums = [
            MockAlbum(1, 'Album 1', 1, 10),
            MockAlbum(2, 'Album 2', 1, 20),
        ]
        mock_store.get_all_albums.return_value = mock_albums
        mock_calc.return_value = 15.0

        response = client.get('/stats/average-tracks')

        # Verify the function was called with correct data structure
        call_args = mock_calc.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0] == {'track_count': 10}
        assert call_args[1] == {'track_count': 20}
