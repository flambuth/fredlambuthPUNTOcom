import spotipy
from datetime import datetime
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

def find_best_result_for_art_name(art_name):
    '''
    Given a string art_name, selects the first artist found by using the .search() method
    of the Spotipy API
    Returns a the JSON from the API request
    '''
    fred_sp_obj = sp_obj()
    search_results = fred_sp_obj.search(art_name, type='artist')
    # 0 index is the best result among the search results
    if search_results['artists']['items']:
        best_result = search_results['artists']['items'][0]
    else:
        best_result = None
    return best_result

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
        self.not_playing_message = f'Nothing is playing on the {self.spotify_username} Spotify account.'
        if self.sp_obj.current_user_playing_track():
            self.currently_playing = self.sp_obj.current_user_playing_track()
        else:
            self.currently_playing = self.not_playing_message
        
    def currently_playing_CSV_entry(self):
        '''
        Returns a dictionary that matches up with the column order of the CSV
        '''
        if self.sp_obj.current_user_playing_track():
            # time info
            timestamp = datetime.fromtimestamp(self.currently_playing['timestamp']/1000)
            
            # song info is in item
            
            spot_item = self.currently_playing['item']
            spotify_id = spot_item['uri'][-22:]
            song_name = spot_item['name']
            song_duration = spot_item['duration_ms']/1000
            
            artists = spot_item['artists'] # a list of dicts
            prim_artist = artists[0]['name']
            if len(artists) > 1:
                feat_artists = artists[1:]
                feat_art_names = [i['name'] for i in feat_artists]
                feat_art_names = ', '.join(feat_art_names)
            else:
                feat_art_names = None
            
            # album info
            album = spot_item['album']
            album_name = album['name']
            album_release_date = album['release_date']
            image_code = album['images'][0]['url'][24:]
            
            keys = ['spotify_id', 'song_name', 'prim_artist', 'feat_artists', 
                    'album_name', 'album_release_date', 'image_code', 'duration', 'timestamp']
            the_list = [spotify_id, song_name, prim_artist, feat_art_names, 
                        album_name, album_release_date, image_code, song_duration, timestamp.isoformat()]
            
            the_dict = {key:value for key,value in zip(keys,the_list)}
            return the_dict
        else:
            return self.not_playing_message
    
    def initialize_csv(self):
        '''Initializes the csv to start recording entries. Only works is a song is active on the Spotify account.'''
        with open(self.db, 'w', newline='') as csvfile:
            initial_data = self.currently_playing_CSV_entry()
            writer = csv.writer(csvfile)

            # Write the header (keys)
            writer.writerow(['id'] + list(initial_data.keys()))

            # Write the row (values)
            writer.writerow([1] + list(initial_data.values()))
        print(f'CSV created in {self.db} directory for {self.spotify_username}')
        
    def latest_song_in_csv(self):
        '''Returns a dictionary of the last row in the input db_path'''
        with open(self.db, 'r') as file:
            reader = csv.DictReader(file)  # Use DictReader to get the rows as dictionaries
            last_row = None
            for row in reader:
                last_row = row  # Iterate through all rows and store the last one
        return last_row
    
    def should_currently_playing_save_to_csv(self):
        '''Returns nothing if no conditions have been met'''
        current_song = self.latest_song_in_csv()
        in_the_csv = self.latest_song_in_csv()
        
        # If its a totally new spotify_id from the last
        if current_song['spotify_id'] != in_the_csv['spotify_id']:
            return True
        
        # If its been longer than the song length since the last time it was played
        iso_dt = datetime.fromisoformat(in_the_csv['timestamp'])
        time_diff = datetime.now() - iso_dt
        time_diff_in_secs = time_diff.total_seconds()
        if time_diff_in_secs > float(in_the_csv['duration']):
            return True
        
    def add_currently_playing_to_csv(self):
        
        if self.should_currently_playing_save_to_csv():
            last_id = self.latest_song_in_csv()['id']
            new_id = int(last_id) + 1
            new_song_data = self.currently_playing_CSV_entry()
            with open(self.db, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([new_id] + list(new_song_data.values()))
                print(f"{new_song_data['song_name']} saved to the CSV")
        else:
            print('Did not meet new song criteria')