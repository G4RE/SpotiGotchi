def get_now_playing(sp):
    playback = sp.current_playback()
    if not playback or not playback.get("item"):
        return None

    item = playback["item"]
    album = item.get("album") or {}
    album_images = album.get("images") or []
    album_art_url = album_images[0]["url"] if album_images else None

    return {
        "track": item["name"],
        "artist": ", ".join(a["name"] for a in item["artists"]),
        "album_art_url": album_art_url,
        "is_playing": playback["is_playing"],
    }
