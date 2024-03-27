import spotipy
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from app.models.charts import recently_played
from app.utils import push_app_context

import json

def get_spot_token_for_user(spotify_username):
    # Load tokens from JSON file
    with open(f'cache-{spotify_username}.json', 'r') as f:
        tokens = json.load(f)
    return tokens['access_token']

def sp_orbNEW(spotify_username):
    '''
    Makes a spotipy object that can make requests to my spot account
    '''
    sp = spotipy.Spotify(
        get_spot_token_for_user(spotify_username)
    )
    return sp


def sp_orb():
    '''
    Makes a spotipy object that can make requests to my spot account
    '''
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            username='lambuth',
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI))
    return sp


def sp_to_rp(sp_current_song):
    '''
    Converts the response you get from the sp requests endpoint 'current_user_playing_track'
    to a recently_played object
    '''
    timestamp = sp_current_song['timestamp']/1000
    dt = datetime.fromtimestamp(timestamp)
    #last_played = dt.strftime("%Y-%m-%dT%H:%M:%S")

    sp_current_song = sp_current_song['item']
    rp = recently_played(
    art_name = sp_current_song['artists'][0]['name'],
    song_name =  sp_current_song['name'],
    song_link = sp_current_song['external_urls']['spotify'],
    image = sp_current_song['album']['images'][0]['url'],
    last_played = dt,
    )
    return rp


class CurrentlyPlaying:
    '''
    Object that checks what is playing on spotify right now
        -is it a song?
        -is it the same as the last song? could be a long one
    Will run on a cron job every 2 minutes to check for new songs
    '''

    def __init__(self):
        self.app = push_app_context()
        self.sp = sp_orb()
        self.latest_rp = recently_played.get_latest_song()
        if self.check_what_type_is_playing():
            self.current_spotify_song = self.sp.current_user_playing_track()
            self.current_rp_on_spot = sp_to_rp(self.current_spotify_song)

    def check_what_type_is_playing(self):
        right_now = self.sp.current_user_playing_track()
        if right_now == None:
            return False

        if right_now['currently_playing_type'] == 'track':
            return True

    def check_for_new_song(
        self,
        ):
        '''
        Compares what comes back from the spotifyAPI as teh current song playing or last
        with the most recent record added to the 
        'recentl_played' model
        '''
        if self.latest_rp.song_link != self.current_rp_on_spot.song_link:
            return True
        
    def add_to_recently_played(self):
        '''
        performs checks to see if song currently playing on spotify is a track different
        then the last one on the database
        if the song is new, a record is added to the 'recently_played' model

        Runs on a cron job every minute.
        '''
        if self.check_what_type_is_playing() and self.check_for_new_song():
            recently_played.add_rp_to_db(self.current_rp_on_spot)
            print('Added to recently_played table')
        else:
            print('No Dice.')

def today_top_chart(table_name):
    '''
    Accepts a string of one of the daily tables, requests the short-term top10 from Spotify, returns a JSON
    '''
    sp

    if table_name=='daily_artists':
        today_top_results = sp.current_user_top_artists(time_range='short_term', limit=10)
    elif table_name=='daily_tracks':
        today_top_results = sp.current_user_top_tracks(time_range='short_term', limit=10)
    return today_top_results


if __name__ == '__main__':
    CurrentlyPlaying().add_to_recently_played()