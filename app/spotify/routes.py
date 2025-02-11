from app.spotify import bp, cache
from flask import render_template, request, redirect, url_for, render_template_string, flash
from flask_login import login_required, current_user
from sqlalchemy import desc

from app.models.charts import recently_played, daily_artists ,daily_tracks
from app.models.catalogs import track_catalog, artist_catalog
from app.models.playlists import Playlists
from app.models.accounts import artist_comments

from app import db

from app.dash_plotlys.plotly_figures import chart_scatter_plotly

from app.spotify.forms import CourseForm
from app.forms import CommentForm, SearchForm

import app.spotify.daily_funcs as daily_funcs
import app.spotify.art_cat_funcs as ac_funcs
from app.spotify.plotly_figs import top_5_artists_fig, top_5_tracks_fig


from datetime import datetime

#YOU CANT HAVE ANYTHING OUTSIDE OF DECORATED ROUTES! Do it somewhere else and import it.
#latest_daily_date = daily_tracks.query.order_by(daily_tracks.id.desc()).first().date
#latest_date_obj = datetime.strptime(latest_daily_date, "%Y-%m-%d").date()


###############################
##Playlists
#@bp.route('/spotify/playlist/<string:playlist_id>', methods=('GET','POST'))
@bp.route('/spotify/playlist', methods=('GET','POST'))
def playlist_homepage():
    '''
    Temp install!
    '''
    #fig = top_5_artists_fig()
    #html = fig.to_html()

    return render_template('spotify/playlist/playlist_timeline.html')

@bp.route('/spotify/playlist/<string:playlist_id>', methods=('GET','POST'))
def playlist_timeline(playlist_id):
    '''
    Temp install!
    '''
    playlist_records = Playlists.filtered_enriched_playlist(playlist_id)
    
    context = {
        'tracks':playlist_records,
    }

    return render_template('spotify/playlist/playlist_timeline.html', **context)


##############################
@bp.route('/spotify/top_five_artists')
@login_required
def top_five_artist_plot():
    '''
    Temp install!
    '''
    fig = top_5_artists_fig()
    html = fig.to_html()

    return render_template_string(html)

@bp.route('/spotify/top_five_tracks')
@login_required
def top_five_tracks_plot():
    '''
    No sidebar!
    '''
    fig = top_5_tracks_fig()
    html = fig.to_html()

    return render_template_string(html)


#############################################
@bp.route('/spotify')
@bp.route('/spotify/')
def spotify_landing_page():
    '''
    I guess this should look flashy and have a menu that offers something the sidebar of the regular Spotify
    views or the art_cat_base do not offer. Or just a very simple menu, but flashier?
    '''
    latest_5 = ac_funcs.latest_art_cats()
    top_5_arts = daily_funcs.top_ever_daily_artists(5)
    top_5_tracks = daily_funcs.top_ever_daily_tracks(5)
    daily_rp_avg = recently_played.rp_average_per_day()

    context = {
        'latest_artists':latest_5,
        'top_5_arts' : top_5_arts,
        'top_5_tracks' : top_5_tracks,
        'daily_rp_avg' : daily_rp_avg,
        
    }
    return render_template('spotify/spotify_homepage.html', **context)


###########################################
# art_cat routes

@bp.route('/spotify/art_cat/', methods=('GET','POST'))
@bp.route('/spotify/art_cat', methods=('GET','POST'))
def art_cat_landing_page():
    form = CourseForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))

    thruples = ac_funcs.genre_landing_thruples()

    context = {
        'thruples' : thruples,
        'form':form,
    }

    return render_template('spotify/art_cat/art_cat_landing.html', **context)


# Adding Comments to artist
@bp.route('/spotify/art_cat/artist/<string:art_id>', methods=('GET','POST'))
def art_cat_profile(art_id):
    form = SearchForm()
    comment_form = CommentForm()

    if (form.validate_on_submit()):
        print('search bar was used')
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))
    
    
    if comment_form.validate_on_submit():
        print('comment was made')
        if not current_user.is_authenticated:
            flash('You must be logged in to add a comment.', 'warning')
            return redirect(url_for('user_accounts.login'))  # Redirect to login page if not logged in
        
        art_comment = artist_comments(
            content=comment_form.content.data,
            artist_catalog_id=art_id,
            user_id=current_user.id,
            comment_date=datetime.utcnow())
        
        db.session.add(art_comment)
        db.session.commit()
        return redirect(url_for('spotify.art_cat_profile', art_id=art_id))

    profile_context = ac_funcs.art_cat_profile(art_id)
    profile_context['form'] = form
    profile_context['comment_form'] = comment_form

    print('profile got GET')
    return render_template('spotify/art_cat/art_cat_profile.html', **profile_context)

#######################
#Three index routes. They need pagination.
#How?

@bp.route('/spotify/art_cat/<string:letter>', methods=('GET','POST'))
def index_by_letter(letter):
    page = request.args.get('page', 1, type=int)
    form = CourseForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))
    
    art_cat_index, total_count = ac_funcs.all_art_cats_starting_with(
        letter,
        page,
        )
    
    context = {
        'art_cat_index' : art_cat_index.items,
        'letter' : letter,
        'form':form,
        'artist_count': total_count,
        'prev_page':art_cat_index.prev_num,
        'next_page':art_cat_index.next_num,
        'first_page':1,
        'last_page':art_cat_index.pages,
    }

    return render_template('spotify/art_cat/art_cat_index.html', **context)



@bp.route('/spotify/art_cat/genre/<string:master_genre>', methods=('GET','POST'))
@bp.route('/spotify/art_cat/genre', defaults={'master_genre': None}, methods=('GET','POST'))
def index_by_genre(master_genre):
    page = request.args.get('page', 1, type=int)
    form = CourseForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))
    
    sort = request.args.get('sort','default')

    if (master_genre in ac_funcs.genres)|(master_genre is None) :
        art_cat_index, ac_count = ac_funcs.all_art_cats_in_master_genre(
            master_genre, 
            page,
            sort
            )    
    else:
        art_cat_index, ac_count = ac_funcs.art_cats_with_this_genre(
            master_genre, 
            page,
            sort,
            )


    context = {
        'genre': master_genre,
        'artist_count': ac_count,
        'art_cat_index': art_cat_index.items,
        'form':form,
        'prev_page':art_cat_index.prev_num,
        'next_page':art_cat_index.next_num,
        'first_page':1,
        'last_page':art_cat_index.pages,
        'sort':sort,
    }

    return render_template('spotify/art_cat/art_cat_index.html', **context)

@bp.route('/spotify/search/<string:search_term>', methods=('GET','POST'))
def index_by_search(search_term):
    form = CourseForm()
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))

    like_arts = ac_funcs.art_cat_name_search(search_term)

    context = {
        'like_arts':like_arts,
        'form':form,
    }

    return render_template('spotify/art_cat/art_cat_search.html', **context)

###########################################
###########################################
#track_cat routes

@bp.route('/spotify/track_cat/', methods=('GET','POST'))
@bp.route('/spotify/track_cat', methods=('GET','POST'))
def track_cat_landing_page():

    thruples = track_catalog.track_cat_landing_thruples()

    context = {
        'thruples' : thruples,
    }

    return render_template('spotify/track_cat/track_cat_landing.html', **context)

@bp.route('/spotify/track_cat/<string:letter>')
def index_tracks_by_letter(letter):
    
    track_index = track_catalog.all_tracks_starting_with(letter)
    
    context = {
        'track_index' : track_index,
        'letter' : letter,
    }

    return render_template('spotify/track_cat/track_index.html', **context)


###############
###########################################
#rp routes
@bp.route('/spotify/yesterday')
@bp.route('/spotify/yesterday/')
@cache.cached(timeout=3600)
def yesterday():
    '''
    Route to the recent template.
    '''
    #three_ago = recently_played.query.all()[-3:]
    yesterday_records = recently_played.past_24_hrs_rps()
    song_count_yesterday = len(yesterday_records)
    distinct_arts = len(list(set([i.art_name for i in yesterday_records])))
    known, unknown = recently_played.scan_for_art_cat_awareness(yesterday_records)
    known_cats = list(map(
        artist_catalog.name_to_art_cat,
        known,
    ))
    sorted_known_cats = sorted(known_cats, key=lambda x: (x.master_genre.lower(), x.art_name.lower()))
    context = {
        #'last_three' : three_ago,
        'yesterday_song_count' : song_count_yesterday,
        'distinct_arts' : distinct_arts,
        'known':known,
        'unknown':sorted(unknown, key=lambda x: (x.lower(), x)),
        'known_cats':sorted_known_cats,
    }
    return render_template('spotify/recently_played.html', **context)

@bp.route('/spotify/right_now')
@bp.route('/spotify/right_now/')
#@cache.cached(timeout=3600)
def right_now():
    '''
    Route to the recent template.
    '''
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagination = recently_played.query.order_by(desc(recently_played.id)).paginate(page=page, per_page=per_page, error_out=False)
    five_ago = pagination.items
    
    cat_scanned = list(map(
        recently_played.cat_scan_rp_object,
        five_ago
    ))

    context = {
        'last_five': cat_scanned,
        'pagination': pagination,
    }

        # Check if there are more items to paginate
    #if pagination.has_next:
        # Increment the page for the next request
    #    session['page'] = page + 1

    return render_template('spotify/recently_playing.html', **context)


#############################################
@bp.route('/spotify/daily/tracks')
@bp.route('/spotify/daily/tracks/')
def latest_daily_tracks():
    latest_date = daily_funcs.latest_daily_date(daily_tracks) 
    tracks = daily_funcs.latest_daily_chart(daily_tracks)

    context = {
        'latest_date' : latest_date,
        'tracks' : tracks,
        'year': latest_date.year,
        'month_num' : latest_date.month,
        'day': latest_date.day,
    }

    return render_template('spotify/latest_tracks.html', **context)

@bp.route('/spotify/daily/artists')
@bp.route('/spotify/daily/artists/')
def latest_daily_artists():
    latest_date = daily_funcs.latest_daily_date(daily_artists)
    arts = daily_funcs.latest_daily_chart(daily_artists)

    context = {
        'latest_date' : latest_date,
        'artists' : arts,
        'year': latest_date.year,
        'month_num' : latest_date.month,
        'day': latest_date.day,
    }

    return render_template('spotify/latest_artists.html', **context)

@bp.route('/spotify/daily/tracks/<string:year>/<string:month>/<string:day>', methods=('GET','POST'))
def tracks_prev(year, month, day):
    date_obj = datetime.strptime(f'{year}-{month}-{day}', "%Y-%m-%d").date()
    context = daily_funcs.archive_chart_context(
        daily_tracks,
        date_obj
    )
    return render_template('spotify/archive_chart_tracks.html', **context)

@bp.route('/spotify/daily/artists/<string:year>/<string:month>/<string:day>', methods=('GET','POST'))
def arts_prev(year, month, day):
    date_obj = datetime.strptime(f'{year}-{month}-{day}', "%Y-%m-%d").date()
    context = daily_funcs.archive_chart_context(
        daily_artists,
        date_obj
    )
    return render_template('spotify/archive_chart_artists.html', **context)


@bp.route('/spotify/genres/', methods=('GET','POST'))
@bp.route('/spotify/genres', methods=('GET','POST'))
def genres_landing_page():
    form = CourseForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))

    book = artist_catalog.genre_dictionary()
    starting_chars = list(set([i[0] for i in book.keys()]))
    starting_alphas = sorted([char for char in starting_chars if char.isalpha() == True])
    alpha_counts = [
    len([genre for genre in book.keys() if genre.startswith(i)]) for i in starting_alphas
    ]

    thruples = list(zip(
        starting_alphas,
        alpha_counts,
    ))

    context = {
        'thruples' : thruples,
        'form':form,
    }

    return render_template('spotify/genre_cat/genre_landing.html', **context)


@bp.route('/spotify/genres/<string:letter>', methods=('GET','POST'))
def alpha_genre_list(letter):
    form = CourseForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        return redirect(url_for('spotify.index_by_search', search_term=form.search_term.data))
    
    blob_list = artist_catalog.all_distinct_genres()
    genre_bookings = { genre: artist_catalog.artists_in_genre(genre) for genre in blob_list}

    # all the genres that start with the 'letter'
    lettered_results = [i for i in genre_bookings.keys() if i.startswith(letter)]
    # the genre_bookings dict filtered to just the keys that are in lettered_results
    filtered_dict = {k: genre_bookings[k] for k in lettered_results if k in genre_bookings}

    genre_count = len(filtered_dict.keys())

    context = {
        'genre_list' : filtered_dict,
        'form':form,
        'letter':letter,
        'genre_count':genre_count,
    }
    return render_template('spotify/genre_cat/genre_alpha_list.html', **context)