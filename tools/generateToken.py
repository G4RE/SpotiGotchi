import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="user-read-playback-state",
        cache_path="../.spotify_cache"
    )
)

print("Token generated successfully")
