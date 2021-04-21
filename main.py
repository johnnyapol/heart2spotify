#!/usr/bin/env python3
"""
    Copyright (c) 2021 John C. Allwein 'johnnyapol'.
    For Licensing information, See LICENSE.txt
"""

from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import quote_plus
from requests import get
from traceback import print_exc
import json


def get_songs(recent_link):
    data = get(recent_link).text

    soup = BeautifulSoup(data)
    data = soup.findAll("li", {"class": "track-list-item"})

    for x in data:
        title = x.find("a", {"class": "track-title"}).text
        artist = x.find("a", {"class": "track-artist"}).text
        album = x.find("a", {"class": "track-album"}).text
        yield (title, album, artist)


def spotify(client_id, client_secret, stations, cache):

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8080",
            scope="playlist-modify-public",
        )
    )

    for station in stations:
        print(f"Processing station: {station}")
        playlist = stations[station]["playlist_url"]
        recent_link = stations[station]["recent_link"]

        try:
            l = set()
            for x in get_songs(recent_link):
                print(x)
                result = sp.search(
                    f"track:{x[0]} album:{x[1]} artist:{x[2]}", type="track", limit=1
                )
                try:
                    l.add(result["tracks"]["items"][0]["id"])
                except:
                    print_exc()
                    print(f"Failed to find a matching song for {x}")

            l = cache.update(station, l)

            if len(l) == 0:
                print("No new songs")
                continue

            sp.playlist_add_items(playlist, l)
        except:
            print(f"Error encountered while updating station {station}")
            print_exc()


def load_config():
    try:
        with open("config.json", "r") as cfg_file:
            config = json.load(cfg_file)
    except:
        print(
            "Failed to handle configuration file. See config.json.sample for instructions"
        )
        print_exc()
        exit(1)

    # Configuration validation
    if "client_id" not in config:
        print("Missing client ID -- exiting!")
        exit(1)

    if "client_secret" not in config:
        print("Missing client secret -- exiting!")
        exit(1)

    if "stations" not in config or len(config["stations"]) == 0:
        print("No stations specified. No work to be done.")
        exit(0)

    # Validate each station:
    for station in config["stations"]:
        data = config["stations"][station]

        if "playlist_url" not in data:
            print(
                f"Station configuration is invalid: playlist_url is missing from station {station}"
            )
            exit(1)
        if "recent_link" not in data:
            print(
                f"Station configuration is invalid: recent_link is missing from station {station}"
            )
            exit(1)

    return (config["client_id"], config["client_secret"], config["stations"])


if __name__ == "__main__":
    from cache_manager import FlatfileCacheManager

    id, secret, stations = load_config()
    spotify(id, secret, stations, FlatfileCacheManager())
