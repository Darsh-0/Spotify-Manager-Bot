#!/usr/bin/env python
import os
import time
from datetime import datetime

import pytz
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

NZ_TZ = pytz.timezone("Pacific/Auckland")

SECONDS_PLAYLIST_URI = "spotify:playlist:6DkO7OwXkfJvYe7Bir422r"
HISTORY_PLAYLIST_ID = "1WyMqjDhkaHPinfdA5Hg1u"  # plain ID is safest


def seconds_since_november_12_2005() -> str:
    november_12_2005_nz = NZ_TZ.localize(datetime(2005, 11, 12))
    current_datetime_nz = datetime.now(NZ_TZ)
    seconds_difference = (current_datetime_nz - november_12_2005_nz).total_seconds()
    return str(round(seconds_difference))


def get_current_date_nz() -> str:
    return str(datetime.now(NZ_TZ).date())


def get_ordinal(day: int) -> str:
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def call_with_retry(fn, *args, **kwargs):
    """
    Retries on Spotify 429 rate-limit using Retry-After header.
    """
    while True:
        try:
            return fn(*args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 1))
                print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                continue
            raise


def update_seconds_playlist(sp: spotipy.Spotify):
    call_with_retry(
        sp.playlist_change_details,
        SECONDS_PLAYLIST_URI,
        name=f"{seconds_since_november_12_2005()} seconds old",
        description="wow it worked",
    )


def get_top_track_id(sp: spotipy.Spotify, playlist_id: str):
    """
    Returns the track ID at position 0, or None if playlist empty/unavailable.
    """
    data = call_with_retry(sp.playlist_tracks, playlist_id, limit=1)
    items = data.get("items", [])
    if not items:
        return None

    track = items[0].get("track")
    if not track:
        return None

    return track.get("id")


def secondly(sp: spotipy.Spotify):
    # 1) Update the "seconds old" playlist
    #update_seconds_playlist(sp)

    # 2) Get currently playing
    current = call_with_retry(sp.current_user_playing_track)
    item = (current or {}).get("item")
    if not item:
        return

    track_id = item.get("id")
    track_uri = item.get("uri")
    if not track_id or not track_uri or not track_uri.startswith("spotify:track:"):
        return

    # 3) Only update playlist if current track is NOT already the top track
    top_id = get_top_track_id(sp, HISTORY_PLAYLIST_ID)
    if top_id == track_id:
        return

    # 4) Move track to top:
    #    simplest approach: remove occurrences then add at position 0
    call_with_retry(sp.playlist_remove_all_occurrences_of_items, HISTORY_PLAYLIST_ID, [track_id])
    call_with_retry(sp.playlist_add_items, HISTORY_PLAYLIST_ID, [track_id], position=0)

    # 5) Update playlist title + description with accurate count + NZ time
    playlist_info = call_with_retry(sp.playlist, HISTORY_PLAYLIST_ID)
    num_tracks = playlist_info["tracks"]["total"]

    title = f"every song i've listened to ({num_tracks} songs so far)"

    now_nz = datetime.now(NZ_TZ)
    formatted = now_nz.strftime("of %B, %Y at %I:%M:%S %p")
    description = f"i last updated this at {get_ordinal(now_nz.day)} {formatted}"

    call_with_retry(sp.playlist_change_details, HISTORY_PLAYLIST_ID, name=title, description=description)


def run_function_every_31_seconds(sp: spotipy.Spotify):
    secondly(sp)
    print("hell")

    while True:
        time.sleep(31)
        secondly(sp)

def build_spotify_client() -> spotipy.Spotify:
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Missing CLIENT_ID or CLIENT_SECRET env vars.")

    scopes = (
        "playlist-modify-private "
        "playlist-modify-public "
        "user-read-currently-playing "
        "user-modify-playback-state "
        "ugc-image-upload "
        "user-top-read"
    )

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://127.0.0.1:8000/callback",
        scope=scopes,
        cache_path="my_data.cache",
        open_browser=False
    ),
    requests_timeout=10,
    )


if __name__ == "__main__":
    #keep_alive()
    sp = build_spotify_client()
    run_function_every_31_seconds(sp)
