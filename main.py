#!/usr/bin/env python
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
import random
from datetime import datetime
import requests

import pytz
import base64

from keep_alive import keep_alive
from spotipy.exceptions import SpotifyException




#time.sleep(99999999)

nz_timezone = pytz.timezone('Pacific/Auckland')

def seconds_since_november_12_2005():
    nz_timezone = pytz.timezone('Pacific/Auckland')
    november_12_2005_nz = nz_timezone.localize(datetime(2005, 11, 12))
    current_datetime_nz = datetime.now(nz_timezone)
    time_difference = current_datetime_nz - november_12_2005_nz
    seconds_difference = time_difference.total_seconds()
    return str(round(seconds_difference))

def get_current_date_nz():
    nz_timezone = pytz.timezone('Pacific/Auckland')
    current_datetime_nz = datetime.now(nz_timezone)
    current_date_nz = current_datetime_nz.date()
    return str(current_date_nz)




def get_top_track():
    top_tracks = sp.current_user_top_tracks(time_range='medium_term', limit=1)
    if len(top_tracks['items']) > 0:
        top_track = top_tracks['items'][0]
        track_name = top_track['name']
        artist_name = top_track['artists'][0]['name']
        return f"{track_name} by {artist_name}"
    else:
        return "No top track found"

def choose_random_file(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")

    all_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    if not all_files:
        raise FileNotFoundError(f"No files found in the folder '{folder_path}'.")

    random_file = random.choice(all_files)

    print(f"The chosen file is: {random_file}")

    return random_file




def change_party_picture():
    try:
        random_photo_path = choose_random_file("photos")
        with open(f'photos/{random_photo_path}', 'rb') as image_file:
            image_data_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        sp.playlist_upload_cover_image("spotify:playlist:6ehqdIStgoHuRQFBnMnj00", image_data_base64)
    except Exception as e:
        print(f"An error occurred: {e}, Retrying in 30 seconds")
        time.sleep(31)
        change_party_picture()
        

def get_ordinal(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"
        


def secondly():
    try:

        sp.playlist_change_details("spotify:playlist:6DkO7OwXkfJvYe7Bir422r", name=f'{seconds_since_november_12_2005()} seconds old', public=None, collaborative=None, description="wow it worked")

        


    except SpotifyException as e:
        retry_after = int(e.headers.get('Retry-After', 1))
        print(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
        time.sleep(retry_after)

    
    

    playlist_id = "spotify:playlist:1WyMqjDhkaHPinfdA5Hg1u"

    current_track_info = sp.current_user_playing_track()
    playlist_tracks = sp.playlist_tracks(playlist_id)
    if current_track_info is not None and 'item' in current_track_info and current_track_info['item'] is not None and 'uri' in current_track_info['item'] and current_track_info != playlist_tracks['items'][0]['track']:
        uri = current_track_info['item']['uri']  
        if uri.startswith('spotify:track:'):
            

            sp.playlist_remove_all_occurrences_of_items(playlist_id, [current_track_info['item']['id']])
            time.sleep(3)
            sp.playlist_add_items(playlist_id, [current_track_info['item']['id']], position=0)



            playlist_info = sp.playlist(playlist_id)
            num_tracks = playlist_info['tracks']['total']

            title = f"every song i've ever listened to ({num_tracks} songs so far)"

            current_datetime_nz = datetime.now(nz_timezone)
            formatted_datetime_nz = current_datetime_nz.strftime('of %B, %Y at %I:%M:%S %p')

            sp.playlist_change_details("spotify:playlist:1WyMqjDhkaHPinfdA5Hg1u", name=title, description=f'Automatically updated on {get_ordinal(current_datetime_nz.day)} {formatted_datetime_nz}')

            
  
def daily():
    #sp.playlist_change_details("spotify:playlist:7obFw2yBRLkdZVSwRASNJr", name=get_joke(), public=None, collaborative=None,description="wow it worked")

    sp.playlist_change_details("spotify:playlist:7obFw2yBRLkdZVSwRASNJr", name=f'i like {get_top_track().lower()}')
    
    change_party_picture()
    
    


#DEVICE_ID_PHONE = os.environ['DEVICE_ID_PHONE']
#DEVICE_ID_COMPUTER = os.environ['DEVICE_ID_COMPUTER']
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')


scopes = "playlist-modify-private,playlist-modify-public, user-read-currently-playing,user-modify-playback-state,ugc-image-upload, user-top-read"
# Spotify Authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                client_secret=CLIENT_SECRET,
                                                redirect_uri="http://localhost:8000/callback/",
                                                scope=scopes,
                                                cache_path='my_data.cache',
                                                requests_timeout=10))



def run_function_every_31_seconds():
    last_execution_time = datetime.now()
    saved_date = get_current_date_nz()

    while True:
        current_time = datetime.now()
        time_difference = current_time - last_execution_time

        if time_difference.total_seconds() >= 31:
            current_date = get_current_date_nz()

            if current_date != saved_date:
                daily()
                saved_date = current_date
            else:
                secondly()

            last_execution_time = current_time

# Run the function

if __name__ == "__main__":
    keep_alive()
    run_function_every_31_seconds()
    









