#!/usr/bin/env python3

from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import quote_plus
from requests import get
from pickle import loads, dumps
from traceback import print_exc


def get_songs(recent_link):
    data = get(recent_link).text

    soup = BeautifulSoup(data)
    data = soup.findAll("li", {"class": "track-list-item"})

    for x in data:
        title = x.find("a", {"class": "track-title"}).text
        artist = x.find("a", {"class": "track-artist"}).text
        album = x.find("a", {"class": "track-album"}).text
        yield (title, album, artist)


def get_cache():
    try:
        with open(".songcache", "rb") as f:
            return loads(f.read())
    except:
        return set()


def save(cache):
    with open(".songcache", "wb") as f:
        f.write(dumps(cache))


def spotify():
    cache = get_cache()
    from secret import client_id, client_secret, playlist, recent_link

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8080",
            scope="playlist-modify-public",
        )
    )
    l = set()
    for x in get_songs(recent_link):
        result = sp.search(
            f"track:{x[0]} album:{x[1]} artist:{x[2]}", type="track", limit=1
        )
        try:
            l.add(result["tracks"]["items"][0]["id"])
        except:
            print_exc()
            print("Failed to handle ", x)

    l = l - cache
    if len(l) == 0:
        print("No new songs")
        return
    cache = cache | l
    save(cache)

    sp.playlist_add_items(playlist, l)


if __name__ == "__main__":
    spotify()
