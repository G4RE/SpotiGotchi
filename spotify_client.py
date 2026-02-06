import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_spotify_client():
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-read-playback-state",
            cache_path=".spotify_cache"
        )
    )
