import os
import time
import pylast
import ytmusicapi
from ytmusicapi.auth.oauth import OAuthCredentials


API_KEY = os.getenv("LASTFM_API_KEY")
API_SECRET = os.getenv("LASTFM_API_SECRET")
USERNAME = os.getenv("LASTFM_USERNAME")
PASSWORD = os.getenv("LASTFM_PASSWORD")

# ============================================================
# 1. BROWSER AUTHENTICATION
# ============================================================

BROWSER_JSON = os.getenv("BROWSER_JSON")

if not BROWSER_JSON:
    raise RuntimeError("BROWSER_JSON secret is missing")

browser_json_path = "browser.json"

with open(browser_json_path, "w") as f:
    f.write(BROWSER_JSON)

ytmusic = ytmusicapi.YTMusic(browser_json_path)


# ============================================================
# 2. OAUTH AUTHENTICATION
# ============================================================

# OAUTH_CLIENT_ID = os.getenv("YT_OAUTH_CLIENT_ID")
# OAUTH_CLIENT_SECRET = os.getenv("YT_OAUTH_CLIENT_SECRET")
# OAUTH_JSON = os.getenv("OAUTH_JSON")
#
# if not OAUTH_JSON:
#     raise RuntimeError("OAUTH_JSON secret is missing")
#
# if not OAUTH_CLIENT_ID:
#     raise RuntimeError("YT_OAUTH_CLIENT_ID secret is missing")
#
# if not OAUTH_CLIENT_SECRET:
#     raise RuntimeError("YT_OAUTH_CLIENT_SECRET secret is missing")
#
# oauth_json_path = "oauth.json"
#
# with open(oauth_json_path, "w") as f:
#     f.write(OAUTH_JSON)
#
# ytmusic = ytmusicapi.YTMusic(
#     oauth_json_path,
#     oauth_credentials=OAuthCredentials(
#         client_id=OAUTH_CLIENT_ID,
#         client_secret=OAUTH_CLIENT_SECRET,
#     ),
# )


# ============================================================

def create_lastfm_client():

    if not all([
        API_KEY,
        API_SECRET,
        USERNAME,
        PASSWORD,
    ]):
        raise RuntimeError("One or more Last.fm secrets are missing")

    password_hash = pylast.md5(PASSWORD)

    return pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=USERNAME,
        password_hash=password_hash,
    )
    

def to_scrobble(entry: dict) -> dict:

    artists = ", ".join(
        artist["name"]
        for artist in entry.get("artists", [])
        if artist.get("name")
    )

    primary_artist = (
        entry["artists"][0]["name"]
        if entry.get("artists")
        else artists
    )

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

    if not tracks:
        print("No tracks to scrobble")
        return

    try:
        network.scrobble_many(tracks)

    except pylast.WSError as e:
        print(f"Error scrobbling tracks: {e}")
        raise

    print(f"Scrobbled {len(tracks)} tracks to Last.fm")
    

def main():

    print(f"ytmusicapi version: {ytmusicapi.__version__}")

    print("Fetching YouTube Music history...")

    history = ytmusic.get_history()

    print(f"Retrieved {len(history)} history entries")

    history = [
        entry
        for entry in history
        if entry.get("played") == "Yesterday"
    ]

    print(f"{len(history)} tracks from yesterday")

    scrobbles = [
        to_scrobble(entry)
        for entry in history
    ]

    lastfm = create_lastfm_client()

    scrobble_tracks(lastfm, scrobbles)


if __name__ == "__main__":
    main()
