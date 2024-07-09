from app.utils import push_app_context

from app.models.catalogs import artist_catalog
from my_spotipy.spotify_catalog import ArtistCatalog

def find_break_points(arr, n=4):
    '''
    Returns a dict of the index points that would break the length of the input array's chunks
    divided by 'n'. 
    '''
    chunk_length = len(arr) // n
    
    index_points = {}
    for i in range(n):
        index_points[i] = chunk_length * i

    index_points[n] = len(arr)

    return index_points


def break_art_cat_into_chunks(arr, breakpoints):
    chunks = {}
    keys = list(breakpoints.keys())
    
    for i in range(len(keys) - 1):
        chunks[i] = arr[breakpoints[keys[i]]:breakpoints[keys[i + 1]]]
        
    return chunks

def art_cat_ids_in_chunks(n_chunks=4):
    arr = artist_catalog.all_art_ids_in_cat()
    breakpoints = find_break_points(arr, n_chunks)
    dict_o_chunks = break_art_cat_into_chunks(
        arr,
        breakpoints
    )
    return dict_o_chunks

def refresh_all_art_cat_entries_CHUNKED(app=push_app_context()):
    four_chunks = art_cat_ids_in_chunks()
    for chunk_index, chunk in four_chunks.items():
        for art_id in chunk:
            new_spot = ArtistCatalog(art_id).new_art_cat_entry()
            artist_catalog.add_refreshed_art_cat_to_db(new_spot)
        print(f"Chunk {chunk_index + 1} finished")
    return 'They Are All Refreshed'

def refresh_all_art_cat_entries(
        app=push_app_context()
):
    my_spot_ids = artist_catalog.all_art_ids_in_cat()
    for art_id in my_spot_ids:
        new_spot = ArtistCatalog(art_id).new_art_cat_entry()
        artist_catalog.add_refreshed_art_cat_to_db(new_spot)
    return 'They Are All Refreshed'

if __name__ == '__main__':
    refresh_all_art_cat_entries_CHUNKED()