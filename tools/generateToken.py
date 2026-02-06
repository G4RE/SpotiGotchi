import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from spotify_client import get_spotify_client

get_spotify_client()
print("Token generated successfully and cached for SpotiGotchi.")
