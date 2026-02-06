def get_now_playing(sp):
    playback = sp.current_playback()
    if not playback or not playback.get("item"):
        return None

    item = playback["item"]
    album_images = item["album"]["images"]

    return {
        "track": item["name"],
        "artist": ", ".join(a["name"] for a in item["artists"]),
        "album_art_url": album_images[0]["url"],
        "is_playing": playback["is_playing"],
    }
