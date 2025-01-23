from app.models.catalogs import artist_catalog, track_catalog
from app.models.charts import daily_tracks
from app.utils import push_app_context

from my_spotipy.spotify_catalog import ArtistCatalog, TrackCatalog
from my_spotipy.spotify_daily import ids_missing_from_art_cat

def scan_and_add_missing_artists(
        app=push_app_context()
):
    '''
    Looks at the two daily charts and identifies missing art_ids
    adds them to the artist_catalog model if they are found
    '''
    if ids_missing_from_art_cat():
        for art_id in ids_missing_from_art_cat():
            new_ac = ArtistCatalog(art_id).new_art_cat_entry()
            #new_ac = list_to_art_cat_obj(dicto)
            artist_catalog.add_new_art_cat_to_db(new_ac)

    else:
        print('No new art_ids found in daily models.')


def scan_and_add_new_tracks(
        app=push_app_context()
):
    '''
    Looks for new tracks. Saves to the db any new ones found in daily tracks
    that were not found in track_catalog
    '''
    new_ids = daily_tracks.song_ids_not_in_track_cat()

    if new_ids:
        for song_id in new_ids:
            spot_result = TrackCatalog(song_id)
            track_catalog.add_new_track_cat_to_db(
                spot_result.new_tc
            )
    else:
        print('No new song_ids found in daily models.')
        
def list_to_art_cat_obj(data_list):
    '''
    DEPRECATED. now a method part of ArtistCatalog
    '''
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


if __name__ == '__main__':
    scan_and_add_missing_artists()
    scan_and_add_new_tracks()