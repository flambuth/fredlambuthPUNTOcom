import spotipy
from config import username, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

import app
my_flask_app = app.create_app()
app_ctx = my_flask_app.app_context()
app_ctx.push()
from app.models.charts import recently_played

def sp_api_orb():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        username=username,
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI))
    return sp

def check_what_type_is_playing():
    right_now = sp.current_user_playing_track()
    if right_now['currently_playing_type'] == 'track':
        return True

def check_for_new_song(
        latest_rp,
        current_song,
):
    '''
    Compares what comes back from the spotifyAPI as teh current song playing or last
    with the most recent record added to the 
    'recentl_played' model
    '''
    if latest_rp != current_song:
        return True
    
sp = sp_api_orb()

right_now = sp.current_user_playing_track()
song_right_now = right_now['item']['external_urls']['spotify']

latest_rp = recently_played.get_latest_song_link()