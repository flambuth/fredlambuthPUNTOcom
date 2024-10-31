from my_spotipy.spotify_object import sp_obj, find_best_result_for_art_name
from my_spotipy.genres import inspect_tri_genres
from datetime import date

from app.models.catalogs import track_catalog, artist_catalog
from app.utils import push_app_context

def three_genre_fields(genre_list):
    '''
    Imputes a None value if there is not enough genre tags in the list
    '''
    result = genre_list[:3]  # Get the first three elements
    while len(result) < 3:
        result.append(None)  
    return result

def three_img_fields(img_list):
    '''
    Imputes null values if there is less than 3 image values
    '''
    result = img_list[:3]  
    result = [i['url'][24:] for i in result]

    # Fill with None if needed
    while len(result) < 3:
        result.append(None) 
    return result

def spot_json_to_list(spot_art_record):

    genres = three_genre_fields(spot_art_record['genres'])
    images = three_img_fields(spot_art_record['images'])

    art_data = [
        spot_art_record['id'],
        spot_art_record['name'],
        spot_art_record['followers']['total'],
        genres[0],
        genres[1],
        genres[2],
        images[0],
        images[1],
        images[2],
    ]
    return art_data

def list_to_art_cat_obj(data_list):
    new_ac = artist_catalog(
        art_id=data_list[0],
        art_name=data_list[1],
        followers=data_list[2],
        genre=data_list[3],
        genre2=data_list[4],
        genre3=data_list[5],
        img_url=data_list[6],
        img_url_mid=data_list[7],
        img_url_sml=data_list[8],
        master_genre=data_list[9],
        app_record_date=data_list[10],
        is_current=data_list[11]
    )
    return new_ac

class ArtistCatalog:

    def __init__(            
            self,
            artist_id,
            spotify_username='lambuth'):
        self.art_id = artist_id

        self.sp = sp_obj(spotify_username)
        self.app = push_app_context()

    @staticmethod
    def art_name_to_art_cat(art_name):
        spot_art_record = find_best_result_for_art_name(art_name)
        art_cat_record = spot_json_to_list(spot_art_record)
        return art_cat_record
    
    def art_id_to_art_cat(self):
        '''
        Calls spotify API for artist info. Then processes the JSON result into a list fitting the art_cat schema.
        '''
        spot_art_record = self.sp.artist(self.art_id)
        art_cat_record = spot_json_to_list(spot_art_record)
        return art_cat_record
    
    def new_entry(
        self,
        corrected_entry=False,
        ):
        '''
        Returns a dictionary that has all the necessary fields to be an entry in the artist catalog
        Makes a Spotify API each time. 
        '''
        today_date = date.today()
        today_string = today_date.strftime('%Y-%m-%d')

        artist_data = self.art_id_to_art_cat()

        #takes the three genre tags from spotify, evalutes each for a 'master_genre'
        #then picks the most common one, or the first one if there is a tie.
        tri_genres = artist_data[3:6]
        artist_data.append(inspect_tri_genres(tri_genres))

        artist_data.append(today_string)

        #by default, new_entry means a first entry or a latest revision,
        #so the corrected_entry parameter defaults to False
        if corrected_entry==True:
            artist_data.append(False)
        else:
            artist_data.append(True)

        return artist_data
    
    def new_art_cat_entry(self):
        new_ac_obj = list_to_art_cat_obj(
            self.new_entry()
        )
        return new_ac_obj
    
    
    
    
class TrackCatalog:

    def __init__(            
            self,
            track_id,
            spotify_username='lambuth'):
        '''
        Temp Object gathering spotify data on one track, then making a track_cat object
        ready to be saved to the db
        '''
        self.track_id = track_id

        self.sp = sp_obj(spotify_username)
        self.app = push_app_context()
        self.spotify_result = self.sp.track(self.track_id)
        self.new_tc = track_catalog(
            art_name=self.spotify_result['artists'][0]['name'],
            album_id=self.spotify_result['album']['id'],
            album_name=self.spotify_result['album']['name'],
            song_id=self.spotify_result['id'],
            song_name=self.spotify_result['name'],
            img_url=self.spotify_result['album']['images'][0]['url'][24:],
            duration=self.spotify_result['duration_ms'],
            app_record_date=date.today().isoformat()
        )