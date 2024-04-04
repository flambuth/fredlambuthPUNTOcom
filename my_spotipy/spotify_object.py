import spotipy

from app.utils import push_app_context
from app.models.charts import recently_played

import json
from datetime import datetime

def get_spot_token_for_user(spotify_username):
    # Load tokens from JSON file
    tokens_directory = os.path.join(os.getcwd(), 'my_spotipy', 'user_tokens')

    #Create JSON file with cache-{spotify_user_name}.json format
    json_file_name = os.path.join(tokens_directory, f'cache-{username}.json')
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
