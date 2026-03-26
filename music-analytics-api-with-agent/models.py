"""Data Models for Music Analytics."""


class Artist:
    """Represents a music artist."""
    
    def __init__(self, artist_id, name):
        self.artist_id = artist_id
        self.name = name
        self.albums = []
    
    def add_album(self, album):
        self.albums.append(album)
    
    def album_count(self):
        return len(self.albums)
    
    def to_dict(self):
        return {
            'artist_id': self.artist_id,
            'name': self.name,
            'album_count': self.album_count()
        }


class Album:
    """Represents a music album."""
    
    def __init__(self, album_id, title, artist_id, track_count=0):
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


class MusicStore:
    """In-memory store for music data."""
    
    def __init__(self):
        self._artists = {}
        self._albums = {}
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample music data."""
        artists_data = [
            (1, 'AC/DC'),
            (2, 'Accept'),
            (3, 'Aerosmith'),
            (4, 'Alanis Morissette'),
            (5, 'Alice In Chains'),
        ]
        
        albums_data = [
            (1, 'For Those About To Rock', 1, 10),
            (2, 'Let There Be Rock', 1, 8),
            (3, 'Balls to the Wall', 2, 10),
            (4, 'Restless and Wild', 2, 9),
            (5, 'Big Ones', 3, 15),
            (6, 'Jagged Little Pill', 4, 13),
            (7, 'Facelift', 5, 12),
            (8, 'Dirt', 5, 13),
        ]
        
        for artist_id, name in artists_data:
            self._artists[artist_id] = Artist(artist_id, name)
        
        for album_id, title, artist_id, track_count in albums_data:
            album = Album(album_id, title, artist_id, track_count)
            self._albums[album_id] = album
            if artist_id in self._artists:
                self._artists[artist_id].add_album(album)
    
    def get_all_artists(self):
        return list(self._artists.values())
    
    def get_artist(self, artist_id):
        return self._artists.get(artist_id)
    
    def get_all_albums(self):
        return list(self._albums.values())
    
    def get_albums_by_artist(self, artist_id):
        return [a for a in self._albums.values() if a.artist_id == artist_id]


music_store = MusicStore()
