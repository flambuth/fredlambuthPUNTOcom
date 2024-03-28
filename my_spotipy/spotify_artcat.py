from my_spotipy.spotify_object import sp_obj
from my_spotipy.genres import inspect_tri_genres
from datetime import date

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

class ArtistCatalog:

    def __init__(            
            self,
            artist_id,
            #app,#result of push_app_context()
            spotify_username='lambuth'):
        self.art_id = artist_id

        self.sp = sp_obj(spotify_username)
        self.app = push_app_context()


    def art_id_to_art_cat(
        self,
        ):
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
    
    
'''
def art_id_to_art_cat(artist_id):

    spot_art_record = sp.artist(artist_id)
    art_cat_record = spot_json_to_list(spot_art_record)
    return art_cat_record
'''