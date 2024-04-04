import spotipy

import json
from my_spotipy.spotify_token_refresh import refresh_token_for_user
from config import basedir


def get_spot_token_for_user(spotify_username):
    # Load tokens from JSON file
    refresh_token_for_user(spotify_username)
    tokens_directory = basedir + '/my_spotipy/user_tokens/'

    #Create JSON file with cache-{spotify_user_name}.json format
    json_file_name = tokens_directory + f'cache-{spotify_username}.json'
    with open(json_file_name, 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def sp_obj(
        spotify_username='lambuth'
        ):
    '''
    Makes a spotipy object that can make requests to my spot account
    '''
    sp = spotipy.Spotify(
        get_spot_token_for_user(spotify_username)
    )
    return sp
