from datetime import datetime
from my_spotipy.spotify_object import sp_obj

def sp_to_rp(sp_current_song, cls):
    '''
    Converts the response you get from the sp requests endpoint 'current_user_playing_track'
    to a recently_played object
    '''
    timestamp = sp_current_song['timestamp']/1000
    dt = datetime.fromtimestamp(timestamp)
    #last_played = dt.strftime("%Y-%m-%dT%H:%M:%S")

    sp_current_song = sp_current_song['item']
    rp = cls(
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

    def __init__(
            self, 
            cls,#recently_played 
            app,#result of push_app_context()
            spotify_username):
        #spotify
        self.spot_username = spotify_username
        self.sp = sp_obj(self.spot_username)

        #flask-model
        self.cls = cls
        self.app = app
        self.latest_rp = cls.get_latest_song()
        if self.check_what_type_is_playing():
            self.current_spotify_song = self.sp.current_user_playing_track()
            self.current_rp_on_spot = sp_to_rp(self.current_spotify_song, cls)

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
            self.cls.add_rp_to_db(self.current_rp_on_spot)
            print('Added to recently_played table')
        else:
            print('No Dice.')

