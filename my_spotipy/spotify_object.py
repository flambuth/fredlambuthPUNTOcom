import spotipy
import datetime
import json
import csv
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

def amys_last_five_songs_recently_played():
    '''returns a simple 5 item data structure of the last five songs Amy has listened to'''
    spotify_user = 'riggle.amy'
    ariggs_sp_obj = sp_obj(spotify_user)
    amys_last_five = ariggs_sp_obj.current_user_recently_played(5)['items']

    song_names = [i['track']['name'] for i in amys_last_five]
    artist_names = [i['track']['artists'][0]['name'] for i in amys_last_five]
    return list(zip(song_names, artist_names))


class Song_Counter:
    def __init__(self, spotify_username, db_path) -> None:
        self.spotify_username = spotify_username
        self.db = db_path
        self.sp_obj = sp_obj(self.spotify_username)
        if self.sp_obj.current_user_playing_track():
            self.currently_playing = self.sp_obj.current_user_playing_track()
        else:
            self.currently_playing = f'Nothing Playing on {self.spotify_username}'
        
    def currently_playing_CSV_entry(self):
        # time info
        timestamp = datetime.datetime.fromtimestamp(self.currently_playing['timestamp']/1000)
        
        # song info is in item
        spot_item = self.currently_playing['item']
        spotify_id = spot_item['uri'][-22:]
        song_name = spot_item['name']
        
        artists = spot_item['artists'] # a list of dicts
        prim_artist = artists[0]['name']
        if len(artists) > 1:
            feat_artists = artists[1:]
            feat_art_names = [i['name'] for i in feat_artists]
        else:
            feat_art_names = None
        
        # album info
        album = spot_item['album']
        album_name = album['name']
        album_release_date = album['release_date']
        image_code = album['images'][0]['url'][24:]
        
        keys = ['spotify_id', 'song_name', 'prim_artist', 'feat_artists', 'album_name', 'album_release_date', 'image_code', 'timestamp']
        the_list = [spotify_id, song_name, prim_artist, feat_art_names, album_name, album_release_date, image_code, timestamp.isoformat()]
        
        the_dict = {key:value for key,value in zip(keys,the_list)}
        return the_dict
    
    def initialize_csv(self):
        '''Initializes the csv to start recording entries'''
        with open(self.db, 'w', newline='') as csvfile:
            initial_data = self.currently_playing_CSV_entry()
            writer = csv.writer(csvfile)

            # Write the header (keys)
            writer.writerow(['id'] + list(initial_data.keys()))

            # Write the row (values)
            writer.writerow([1] + list(initial_data.values()))
        print(f'CSV created in {self.db} directory for {self.spotify_username}')