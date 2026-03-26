"""Music Analytics Functions."""


def calculate_album_stats(albums, min_tracks=5, multiplier=1.2):
    """Process album data and return statistics for qualifying albums.
    
    Filters albums with track counts above min_tracks, applies a popularity
    multiplier, and returns the top 5 albums sorted by adjusted popularity.
    """
    output = []
    for album in albums:
        track_count = album.get('track_count', 0)
        if track_count > min_tracks:
            adjusted_popularity = album.get('popularity', 0) * multiplier
            tier = 'platinum' if adjusted_popularity > 80 else 'gold'
            output.append({
                'album_id': album['album_id'],
                'title': album['title'],
                'original_popularity': album.get('popularity', 0),
                'adjusted_popularity': adjusted_popularity,
                'tier': tier
            })
    return sorted(output, key=lambda x: x['adjusted_popularity'], reverse=True)[:5]


def calculate_average_tracks(albums):
    """Calculate average number of tracks per album.
    
    Returns the average track count across all albums.
    """
    total = sum(album.get('track_count', 0) for album in albums)
    return total  # Bug: should return total / len(albums)

    # Bug reproduction:
    # albums = [{'track_count': 10}, {'track_count': 12}, {'track_count': 8}]
    # print(calculate_average_tracks(albums))  # Returns 30, should return 10
