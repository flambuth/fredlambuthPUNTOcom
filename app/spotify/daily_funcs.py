from app.models.charts import daily_artists, daily_tracks
from app.models.catalogs import artist_catalog
from app import db

from sqlalchemy import func
from datetime import timedelta

def daily_chart_joined_art_cat(
        chart_model,
        chart_date_obj,
        ):
    '''
    attaches genre and image data from the art_cat table to the daily chart
    '''
    #subquery is needed to filter down to latest art_cat record when joining
    #to the daily chart
    subquery = artist_catalog.get_current_records().subquery()

    results = chart_model.query.filter(
        chart_model.date == chart_date_obj
        ).outerjoin(
            subquery, 
            chart_model.art_id==subquery.c.art_id
        ).add_columns(
        subquery.c.genre,
        subquery.c.genre2,
        subquery.c.master_genre,
        subquery.c.img_url_sml
        )
    return results

def latest_daily_date(chart_model):
    '''
    Returns a date object for the row with the largest ID
    '''
    latest_date = chart_model.query.order_by(chart_model.id.desc()).first().date
    return latest_date

def latest_daily_chart(chart_model):
    '''
    Uses the latest_daily_date to filter the rows that have the same date. SHould be 10 per daily_type 
    '''
    latest_date = latest_daily_date(chart_model)

    tracks = daily_chart_joined_art_cat(
        chart_model,
        latest_date
        )
    return tracks

def archive_chart_context(
        chart_model,
        date_obj):

    records = daily_chart_joined_art_cat(
        chart_model,
        date_obj
    )
    if not records:
        # Custom message when no data is found
        return "No data found for the specified date."
    
    if chart_model == daily_tracks:
        chart_type = 'Tracks'
    elif chart_model == daily_artists:
        chart_type = 'Artists'
    else:
        chart_type = None

    context = {
        'chart_type' : chart_type,
        'records' : records,
        'date_obj' : date_obj,
        'date_back_1month' : date_obj - timedelta(days=28),
        'date_back_1day' : date_obj - timedelta(days=1),
        'date_fwd_1month' : date_obj + timedelta(days=28),
        'date_fwd_1day' : date_obj + timedelta(days=1),
    }
    return context

def top_ever_daily_artists(
        num=10):
    cream = db.session.query(
    daily_artists.art_name,
    func.count().label('Chart Days')
    ).group_by(daily_artists.art_name
    ).order_by(func.count().desc()
    ).limit(num).all()
    return cream

def top_ever_daily_tracks(
        num=10):
    cream = db.session.query(
    daily_tracks.song_name,
    func.count().label('Chart Days')
    ).group_by(daily_tracks.song_name
    ).order_by(func.count().desc()
    ).limit(num).all()
    return cream

def artist_days_on_charts(
        art_id,
        chart_type):
    '''
    uses the actual model object as the chart_type parameter

    art_name is just the string title of the artist
    '''
    art_days = chart_type.query.filter(chart_type.art_id == art_id).all()
    return art_days

def artist_days_on_both_charts(
        art_id
    ):
    tracks_days = artist_days_on_charts(art_id, daily_tracks)
    arts_days = artist_days_on_charts(art_id, daily_artists)
    return tracks_days + arts_days

def notable_tracks(
        art_name
    ):
    '''
    Returns a list of strings for each unique song in the daily_tracks for the given artist
    Returns None if there aren't any track hits for the given artist
    '''
    track_hits = artist_days_on_charts(
        art_name,
        daily_tracks
    )

    if track_hits:
        track_titles = [i.song_name for i in track_hits]
        track_ids = [i.song_id for i in track_hits]
        return list(set(zip(track_titles, track_ids)))
    else:
        return None

    
def is_one_hit_wonder(
        art_name
    ):
    has_art_days = artist_days_on_charts(art_name, daily_artists)
    if has_art_days:
        return False
    
    track_hits = notable_tracks(art_name)
    if track_hits:
        return False
    else:
        return 'One Hit Wonder'



def find_streaks_in_dates(list_of_dateObjs):
    '''
    Given a list of datetime objects, returns a dictionary with all the streaks as key pairs.
    start date is key, length in days as integer is the value
    '''
    streaks = {}
    current_streak_start = None

    for date in list_of_dateObjs:
        # starts the loop
        if current_streak_start is None:
            current_streak_start = date
            current_streak_length = 1
        # if the next values is just one day forward since the last, streak goes up 1 and the loop moves on to the next iterable
        elif date == current_streak_start + timedelta(days=current_streak_length):
            current_streak_length += 1
        else:
            # the end of a streak writes to a dictionary. key is streak_start_date, value is the length of days the streak was
            if current_streak_length > 1:  # Add this condition to exclude streaks of just one day
                streaks[current_streak_start.isoformat()] = current_streak_length
            current_streak_start = date
            current_streak_length = 1

    # Add the last streak to the dictionary if there is one and it's not just one day
    if current_streak_start is not None and current_streak_length > 1:
        streaks[current_streak_start.isoformat()] = current_streak_length

    return streaks

