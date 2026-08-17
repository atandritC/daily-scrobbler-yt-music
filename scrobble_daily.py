import os
import time
import pylast
import ytmusicapi
from ytmusicapi.auth.oauth import OAuthCredentials

API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
username = os.getenv("LASTFM_USERNAME")
password_hash = pylast.md5(os.getenv("LASTFM_PASSWORD"))

OAUTH_CLIENT_ID = os.getenv("YT_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("YT_OAUTH_CLIENT_SECRET")


def to_scrobble(entry: dict) -> dict:
    artists = ", ".join(a["name"] for a in entry.get("artists") if a.get("id") or [])
    primary_artist = entry["artists"][0]["name"] if entry.get("artists") else artists
    album = (entry.get("album") or {}).get("name", "")
    duration_seconds = entry.get("duration_seconds", 180)
    return {
        "artist": artists,
        "title": entry["title"],
        "timestamp": int(time.time()),
        "album": album,
        "duration": duration_seconds,
        "album_artist": primary_artist,
    }


def scrobble_tracks(network: pylast.LastFMNetwork, tracks: list):
    try:
        network.scrobble_many(tracks)
    except pylast.WSError as e:
        print(f"Error scrobbling tracks: {e}")
        raise
    print(f"Scrobbled {len(tracks)} tracks to Last.fm")


def main():
    oauth_json_path = "oauth.json"
    oauth_json_raw = os.getenv("OAUTH_JSON")
    if not os.path.exists(oauth_json_path):
        with open(oauth_json_path, "w") as f:
            f.write(oauth_json_raw or "{}")

    ytmusic = ytmusicapi.YTMusic(
        oauth_json_path,
        oauth_credentials=OAuthCredentials(
            client_id=OAUTH_CLIENT_ID,
            client_secret=OAUTH_CLIENT_SECRET,
        ),
    )

    lastfm = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=username,
        password_hash=password_hash,
    )

    history = ytmusic.get_history()
    history = [entry for entry in history if entry.get("played") == "Yesterday"]
    scrobbles = [to_scrobble(entry) for entry in history]
    print(f"{len(scrobbles)} tracks to scrobble")
    scrobble_tracks(lastfm, scrobbles)


if __name__ == "__main__":
    main()
