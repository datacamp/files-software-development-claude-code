"""Unit tests for the Music Analytics API routes in routes.py.

Each test swaps `routes.music_store` for a mock filled with real `Artist` and
`Album` objects, so the routes are tested in isolation from the built-in
sample data.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest
from flask.testing import FlaskClient

from app import app
from models import Album, Artist, MusicStore


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    """Provide a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def store() -> Iterator[MagicMock]:
    """Replace the module-level music store used by the routes with a mock."""
    with patch("routes.music_store", spec=MusicStore) as mock_store:
        yield mock_store


def make_album(album_id: int, track_count: int, artist_id: int = 1) -> Album:
    """Build an album with a predictable title."""
    return Album(album_id, f"Album {album_id}", artist_id, track_count)


# --- GET /artists ------------------------------------------------------------


def test_get_artists_returns_all_artists(client: FlaskClient, store: MagicMock) -> None:
    """Every artist in the store is returned, serialised with to_dict()."""
    acdc = Artist(1, "AC/DC")
    acdc.add_album(make_album(1, 10))
    store.get_all_artists.return_value = [acdc, Artist(2, "Accept")]

    response = client.get("/artists")

    assert response.status_code == 200
    assert response.get_json() == [
        {"artist_id": 1, "name": "AC/DC", "album_count": 1},
        {"artist_id": 2, "name": "Accept", "album_count": 0},
    ]


def test_get_artists_empty_store_returns_empty_list(
    client: FlaskClient, store: MagicMock
) -> None:
    """An empty store gives 200 with an empty list, not an error."""
    store.get_all_artists.return_value = []

    response = client.get("/artists")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_artists_rejects_post(client: FlaskClient, store: MagicMock) -> None:
    """The endpoint is read-only: POST is not allowed."""
    response = client.post("/artists", json={"name": "New Artist"})

    assert response.status_code == 405


# --- GET /artists/<artist_id> ------------------------------------------------


def test_get_artist_found(client: FlaskClient, store: MagicMock) -> None:
    """An existing artist is returned and looked up by its integer ID."""
    store.get_artist.return_value = Artist(3, "Aerosmith")

    response = client.get("/artists/3")

    assert response.status_code == 200
    assert response.get_json() == {
        "artist_id": 3,
        "name": "Aerosmith",
        "album_count": 0,
    }
    store.get_artist.assert_called_once_with(3)


def test_get_artist_not_found_returns_404(
    client: FlaskClient, store: MagicMock
) -> None:
    """An unknown ID gives 404 with an error message."""
    store.get_artist.return_value = None

    response = client.get("/artists/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Artist not found"}


@pytest.mark.parametrize("bad_id", ["abc", "-1", "1.5"])
def test_get_artist_non_integer_id_returns_404(
    client: FlaskClient, store: MagicMock, bad_id: str
) -> None:
    """IDs that aren't non-negative integers don't match the route at all."""
    response = client.get(f"/artists/{bad_id}")

    assert response.status_code == 404
    store.get_artist.assert_not_called()


# --- GET /artists/<artist_id>/albums -----------------------------------------


def test_get_artist_albums_returns_albums(
    client: FlaskClient, store: MagicMock
) -> None:
    """The artist's albums are returned, filtered by the given artist ID."""
    store.get_albums_by_artist.return_value = [make_album(1, 10), make_album(2, 8)]

    response = client.get("/artists/1/albums")

    assert response.status_code == 200
    assert response.get_json() == [
        {"album_id": 1, "title": "Album 1", "artist_id": 1, "track_count": 10},
        {"album_id": 2, "title": "Album 2", "artist_id": 1, "track_count": 8},
    ]
    store.get_albums_by_artist.assert_called_once_with(1)


def test_get_artist_albums_unknown_artist_returns_empty_list(
    client: FlaskClient, store: MagicMock
) -> None:
    """An unknown artist gives 200 and an empty list (current behaviour).

    Unlike GET /artists/<id>, this route doesn't check that the artist exists,
    so it can't tell "no albums" apart from "no such artist".
    """
    store.get_albums_by_artist.return_value = []

    response = client.get("/artists/999/albums")

    assert response.status_code == 200
    assert response.get_json() == []
    store.get_artist.assert_not_called()


# --- GET /albums -------------------------------------------------------------


def test_get_albums_returns_all_albums(client: FlaskClient, store: MagicMock) -> None:
    """Every album in the store is returned."""
    store.get_all_albums.return_value = [make_album(1, 10), make_album(5, 15, 3)]

    response = client.get("/albums")

    assert response.status_code == 200
    assert [a["album_id"] for a in response.get_json()] == [1, 5]


def test_get_albums_empty_store_returns_empty_list(
    client: FlaskClient, store: MagicMock
) -> None:
    """An empty store gives 200 with an empty list."""
    store.get_all_albums.return_value = []

    response = client.get("/albums")

    assert response.status_code == 200
    assert response.get_json() == []


# --- GET /stats/albums -------------------------------------------------------


def test_album_stats_passes_derived_popularity_to_analytics(
    client: FlaskClient, store: MagicMock
) -> None:
    """The route builds dicts with popularity = track_count * 5 for the analytics."""
    store.get_all_albums.return_value = [make_album(1, 10), make_album(2, 3)]

    with patch("routes.calculate_album_stats", return_value=[]) as stats:
        client.get("/stats/albums")

    stats.assert_called_once_with(
        [
            {"album_id": 1, "title": "Album 1", "track_count": 10, "popularity": 50},
            {"album_id": 2, "title": "Album 2", "track_count": 3, "popularity": 15},
        ]
    )


def test_album_stats_end_to_end_values(client: FlaskClient, store: MagicMock) -> None:
    """Popularity is scaled by 1.2 and tiered: above 80 is platinum, else gold.

    15 tracks -> 75 * 1.2 = 90 (platinum); 10 tracks -> 50 * 1.2 = 60 (gold).
    """
    store.get_all_albums.return_value = [make_album(1, 10), make_album(2, 15)]

    response = client.get("/stats/albums")

    assert response.status_code == 200
    result = response.get_json()
    assert [r["album_id"] for r in result] == [2, 1]
    assert result[0]["tier"] == "platinum"
    assert result[0]["adjusted_popularity"] == pytest.approx(90.0)
    assert result[1]["tier"] == "gold"
    assert result[1]["original_popularity"] == 50


def test_album_stats_excludes_albums_with_five_or_fewer_tracks(
    client: FlaskClient, store: MagicMock
) -> None:
    """Only albums with more than 5 tracks qualify (5 is the boundary)."""
    store.get_all_albums.return_value = [make_album(1, 5), make_album(2, 6)]

    response = client.get("/stats/albums")

    assert [r["album_id"] for r in response.get_json()] == [2]


def test_album_stats_returns_at_most_five_albums(
    client: FlaskClient, store: MagicMock
) -> None:
    """Only the top 5 albums by adjusted popularity are returned."""
    store.get_all_albums.return_value = [make_album(i, 5 + i) for i in range(1, 8)]

    response = client.get("/stats/albums")

    assert [r["album_id"] for r in response.get_json()] == [7, 6, 5, 4, 3]


def test_album_stats_empty_store_returns_empty_list(
    client: FlaskClient, store: MagicMock
) -> None:
    """With no albums, the stats endpoint returns an empty list."""
    store.get_all_albums.return_value = []

    response = client.get("/stats/albums")

    assert response.status_code == 200
    assert response.get_json() == []


# --- GET /stats/average-tracks -----------------------------------------------


def test_average_tracks_returns_mean(client: FlaskClient, store: MagicMock) -> None:
    """The average track count across all albums is returned."""
    store.get_all_albums.return_value = [
        make_album(1, 10),
        make_album(2, 12),
        make_album(3, 8),
    ]

    response = client.get("/stats/average-tracks")

    assert response.status_code == 200
    assert response.get_json() == {"average_tracks": 10.0}


def test_average_tracks_returns_fraction(client: FlaskClient, store: MagicMock) -> None:
    """Non-whole averages are returned as floats, not rounded."""
    store.get_all_albums.return_value = [make_album(1, 10), make_album(2, 13)]

    response = client.get("/stats/average-tracks")

    assert response.get_json() == {"average_tracks": 11.5}


@pytest.mark.xfail(
    raises=ZeroDivisionError,
    strict=True,
    reason="Known bug: calculate_average_tracks divides by len(albums) without a guard",
)
def test_average_tracks_empty_store_returns_zero(
    client: FlaskClient, store: MagicMock
) -> None:
    """With no albums, the endpoint should return 0 instead of crashing."""
    store.get_all_albums.return_value = []

    response = client.get("/stats/average-tracks")

    assert response.get_json() == {"average_tracks": 0}
