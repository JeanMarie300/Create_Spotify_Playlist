import requests
from bs4 import BeautifulSoup
import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials

date = ""

while len(date) == 0:
    date = input(
        "From which week of the Billboard 100 would you like to make a playlist off ? Type the date in this format YYYY-MM-DD \n")

URL = f'https://www.billboard.com/charts/hot-100/{date}'

playlist_name = date + " Billboard 100"

response = requests.get(url=URL)

billboard_data = BeautifulSoup(response.text, 'html.parser')

songs_data = billboard_data.select(".o-chart-results-list__item h3")

songs_title = [song.get_text().lstrip().rstrip() for song in songs_data]

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

auth = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope="playlist-modify-private",
                                   redirect_uri="http://example.com")

spotipy_client = spotipy.client.Spotify(auth_manager=auth)

# Used to make the api request
access_token = auth.get_cached_token()['access_token']

user_id = spotipy_client.current_user()['id']

header = {
    "Authorization":f"Bearer {access_token}"
}

spotify_endpoint = 'https://api.spotify.com/v1/search'
songs_uri = []

for title in songs_title:
    params = {
        "q":f"track: {title} year: {date[:4]}",
        "type":"track",
        "limit":1
    }

    response = requests.get(url=spotify_endpoint, headers=header, params=params)

    songs_uri.append(response.json()['tracks']['items'][0]['uri'])

playlist = spotipy_client.user_playlist_create(user_id, playlist_name, public=False, collaborative=False)

spotipy_client.playlist_add_items(playlist['id'], songs_uri)
