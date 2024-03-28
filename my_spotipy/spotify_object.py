import spotipy

from app.utils import push_app_context
from app.models.charts import recently_played

import json
from datetime import datetime

def get_spot_token_for_user(spotify_username):
    # Load tokens from JSON file
    with open(f'cache-{spotify_username}.json', 'r') as f:
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
