from app.models.catalogs import artist_catalog
from app.models.accounts import artist_comments
from app import db
from app.spotify.daily_funcs import artist_days_on_both_charts, find_streaks_in_dates, notable_tracks, is_one_hit_wonder
from sqlalchemy import func, or_

#latest_art_cats = artist_catalog.query.order_by(artist_catalog.app_record_date.desc()).limit(5).all()

genres = ['electronic', 'pop', 'country', 'funk', 'punk', 'indie', 'rock', 'old', 'other']
#alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
non_alphas =  non_alphas = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '@', '#', '$', '%', '&', '*', '!', '?', '+', '-', '[']

def possible_alphas(art_cats_model):
    '''
    Given a flask-sqlAlchemy of artist_catalog, returns a set of all possible charcters for the starting character of each art_name in the art_cat table 
    '''
    art_cats = art_cats_model.query.all()
    all_letters = [i.art_name[0].upper() for i in art_cats]
    unique_chars = list(set(all_letters))
    return sorted(unique_chars, key=lambda x: (not x.isalpha(), x))



############
#Indexing functions, Alpha, master_genre, and sub-genre
def all_art_cats_starting_with(letter):
    
    start_with_letter = artist_catalog.get_current_records().filter(
        artist_catalog.art_name.startswith(letter)
            ).order_by('art_name').all()

    thes = artist_catalog.get_current_records().filter(
        func.substring(artist_catalog.art_name,0,5)=='The '
        ).filter(func.substring(artist_catalog.art_name,6,-1).startswith(letter)
                ).order_by('art_name').all()
    
    art_cat_results = start_with_letter + thes
    return art_cat_results


def all_art_cats_in_master_genre(master_genre):
    if master_genre is not None:
        arts_in_the_genre = artist_catalog.get_current_records().filter(
            artist_catalog.master_genre == master_genre
            ).order_by('art_name'
                       ).all()
    else:
        arts_in_the_genre = artist_catalog.get_current_records().filter(
            artist_catalog.master_genre.is_(None)
            ).order_by(artist_catalog.art_name
                       ).all()


    return arts_in_the_genre

def art_cats_with_this_genre(searched_genre):
    search_term_lower = searched_genre.lower()  # Convert search term to lowercase

    matching_arts = (
        artist_catalog.get_current_records()
        .filter(
            or_(
                func.lower(artist_catalog.genre).like(f"%{search_term_lower}%"),
                func.lower(artist_catalog.genre2).like(f"%{search_term_lower}%"),
                func.lower(artist_catalog.genre3).like(f"%{search_term_lower}%")
            )
        )
        .all()
    )
    return matching_arts



############
#Homepage Level Statistics
def latest_art_cats(num=5):
    '''
    Last five artists added to the art_cat table
    '''
    latest_acs = artist_catalog.query.order_by(artist_catalog.id.desc()).limit(num).all()
    return latest_acs

def art_cat_artist_count():
    '''
    Integer count of all unique artists in the art_cat model
    '''
    return artist_catalog.get_current_records().count()

def art_cat_genre_group_counts():
    '''
    Returns the 9 genres with their count of unique artists in each 'master_genre'
    '''
    genre_group_counts = db.session.query(
        artist_catalog.master_genre,
        func.count().label('Chart Days')
        ).group_by(artist_catalog.master_genre
        ).order_by(func.count().desc()
        ).all()
    return genre_group_counts

def genre_landing_thruples():
    '''
    Returns 9 tuples. Each have a master genre, number of unique artists, and a random artist img_url for teh genre
    '''
    counts = artist_catalog.count_active_records_by_genre()
    genre_img_urls = [random_artist_in_genre(i[0]).img_url_mid for i in counts]
    thruples = list(zip(
    [i[0] for i in counts], [i[1] for i in counts], genre_img_urls
    ))
    return thruples

####################
#Search stuff
def art_cat_name_search(search_term):
    '''
    Needs to deal with nulls
    '''
    like_arts_blob = artist_catalog.art_name.like(f"%{search_term}%")
    like_arts = artist_catalog.get_current_records().filter(like_arts_blob).order_by('art_name').all()
    return like_arts

#####################
#single art_cat functions
def get_one_artist(art_name):
    '''
    Get just one art_cat record
    '''
    uno_art_cat = (
        artist_catalog.query.filter(artist_catalog.art_name == art_name
        ).first())
    return uno_art_cat


def random_artist_in_genre(genre):
    '''
    Adds some randomness to pick from one genre.
    '''
    rando = (
    artist_catalog.query.filter(artist_catalog.master_genre == genre
    ).order_by(func.random()
    ).limit(1).first()
    )
    return rando

def art_id_to_art_cat(art_id):
    '''
    Get just one art_cat record
    '''
    uno_art_cat = (
        artist_catalog.query.filter(artist_catalog.art_id == art_id
        ).first())
    return uno_art_cat

def art_cat_profile(art_id):
    '''
    Returns a dict or obj that has all the values of an art_name that will be displayed on a the art_cat_profile template
    '''
    art_cat_obj = art_id_to_art_cat(art_id)

    both_charts = artist_days_on_both_charts(art_cat_obj.art_id)
    dates = [i.date for i in both_charts]

    #USER COMMENTS
    comments = artist_comments.query.filter_by(artist_catalog_id=art_id).all()

    art_profile_context = {
        'art_id':art_id,
        'art_name':art_cat_obj.art_name,
        'genre1':art_cat_obj.genre,
        'genre2':art_cat_obj.genre2,
        'genre3':art_cat_obj.genre3,
        'img_url':art_cat_obj.img_url,
        'img_url_mid':art_cat_obj.img_url_mid,
        'img_url_sml':art_cat_obj.img_url_sml,
        'followers':art_cat_obj.followers,

        'total_days_on_charts':len(both_charts),

        'first_appearance' : min(dates),
        'last_appearance' : max(dates),
        'streaks':find_streaks_in_dates(dates),

        #tuple! first is the track_name, second is the track_id for Spotify API
        'notable_tracks': notable_tracks(art_cat_obj.art_name),
        'is_one_hit_wonder': is_one_hit_wonder(art_cat_obj.art_name),
        'comments':comments,
    }

    return art_profile_context


