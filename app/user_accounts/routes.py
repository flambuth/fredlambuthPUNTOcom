from app.user_accounts import bp
from app.forms import LoginForm, RegistrationForm, SubmitPictureForm
from app.extensions import db
from app.utils import resize_imageOLD, resize_image
from app.models.accounts import user_accounts, blog_comments

from werkzeug.exceptions import RequestEntityTooLarge
from operator import attrgetter
from urllib.parse import urlsplit
import random

from werkzeug.utils import secure_filename
import os

from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, request, redirect, url_for, flash, current_app, session

#############################
#spot_login_stuff
import json
import config
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from my_spotipy.spotify_token_refresh import refresh_token_for_user
######################
@bp.route('/spotify_login')
#@login_required
def spotify_login():
    session.clear()
    scope = config.scope
    sp_oauth = SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID,
                            client_secret=config.SPOTIPY_CLIENT_SECRET,
                            redirect_uri=config.SPOTIPY_REDIRECT_URI,
                            scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@bp.route('/spotify_callback')
#@login_required
def spotify_callback():
    scope = config.scope
    sp_oauth = SpotifyOAuth(client_id=config.SPOTIPY_CLIENT_ID,
                            client_secret=config.SPOTIPY_CLIENT_SECRET,
                            redirect_uri=config.SPOTIPY_REDIRECT_URI,
                            scope=scope)
    code = request.args.get('code')
    
    #exchanges the authorization code for an access token and a refresh token.
    token_info = sp_oauth.get_access_token(code)
    
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']

    # Store tokens securely (e.g., in session, database)
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    return redirect('/spotify_success')

@bp.route('/spotify_success')
#@login_required
def spotify_success():
    # Retrieve tokens from the session
    access_token = session.get('access_token')
    
    if not access_token:
        # Handle case where access token is not available
        return redirect('/spotify_login')

    # Initialize Spotipy with the obtained access token
    sp = spotipy.Spotify(auth=access_token)

    # Retrieve user's profile information including username
    user_info = sp.current_user()
    username = user_info.get('id')

    results = sp.current_user_top_artists()
    # Process the data and render a page with the user's saved tracks

    # Store tokens, including the username, securely
    tokens = {
        'access_token': access_token,
        'refresh_token': session.get('refresh_token'),
        'username': username
    }

    tokens_directory = os.path.join(os.getcwd(), 'my_spotipy', 'user_tokens')

    #Create JSON file with cache-{spotify_user_name}.json format
    json_file_name = os.path.join(tokens_directory, f'cache-{username}.json')
    with open(json_file_name, 'w') as f:
        json.dump(tokens, f)

    if results:
        return results
    else:
        return "No results for user_top_artists"

@bp.route('/spotify/user/<username>')
@login_required
def success_for_this_user(username):
    # Construct the filename for the JSON file based on the username
    tokens_directory = os.path.join(os.getcwd(), 'my_spotipy', 'user_tokens')

    # Construct the filename for the JSON file based on the username
    json_filename = os.path.join(tokens_directory, f'cache-{username}.json')

    # Read tokens from the JSON file
    try:
        with open(json_filename, 'r') as f:
            tokens = json.load(f)
    except FileNotFoundError:
        # Handle case where the JSON file for the specified user is not found
        return "User not found"

    access_token = tokens.get('access_token')

    if not access_token:
        # Handle case where access token is not available
        return redirect('/spotify_login')

    # Attempt to refresh the access token
    refresh_success = refresh_token_for_user(username)

    if refresh_success:
        # If token refresh was successful, update the access token
        with open(json_filename, 'r') as f:
            tokens = json.load(f)
        access_token = tokens.get('access_token')

        # Use the refreshed access token to make API requests
        sp = spotipy.Spotify(auth=access_token)

        # Example: Get user's currently playing track
        results = sp.current_user_playing_track()
        if results:
            return f"User currently listening to: {results['item']['name']} by {results['item']['artists'][0]['name']} with a refreshed token"
        else:
            return 'No new song'
    else:
        return 'Token refresh failed'



###########################
#######LOGIN, LOGOUT, Register_new_user
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))

    form = LoginForm()

    if form.validate_on_submit():
        user = user_accounts.query.filter_by(username=form.username.data).first()

        #if there is no users of if the password doesn't check out
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user_accounts.login'))

        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('user_accounts.account')
            return redirect(next_page)

    return render_template('accounts/login.html', title='Sign In', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    
    if request.method == 'POST':
        logout_user()
        flash('You have been logged out.')
        return redirect(url_for('homepage'))

    return render_template('accounts/logout.html')

@bp.route('/account', methods=['GET', 'POST'])
def account():
    '''
    Login or make a new account.
    '''
    return render_template('accounts/account_options.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user_accounts.user_page'))

    form = RegistrationForm()

    if form.validate_on_submit():
        print("Form data:", form.data)

        # Check if the provided account creation password is correct
        account_creation_password = form.account_creation_password.data
        required_password = current_app.config.get('BLOG_PSWD')

        if account_creation_password != required_password:
            flash('Invalid account creation password.')
            return redirect(url_for('user_accounts.register'))

        # because the auto_increasing id stopped for this table. I dunno why? 2024_02_24
        rando_id = random.randint(100000, 999999)

        if form.profile_picture.data:
            filename = secure_filename(form.username.data + '.' + form.profile_picture.data.filename.rsplit('.', 1)[1].lower())

            # Constructing the final paths
            input_path = config.basedir + '/app/static/img/user_pics/placeholder.jpg'  # Placeholder file
            output_path = config.basedir + '/app/static/img/user_pics/' + filename

            print("Input Path:", input_path)
            print("Output Path:", output_path)

            # Save and resize the uploaded file
            form.profile_picture.data.save(input_path)
            print("File saved to input path")

            resize_imageOLD(input_path, output_path)
            print("File resized and saved to output path")

        password_hash = user_accounts.set_password(form.password.data)

        new_user = user_accounts(
            id=rando_id,
            username=form.username.data,
            email=form.email.data,
            password_hash=password_hash)

        db.session.add(new_user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        # login_user(new_user)  # Automatically log in the new user after registration
        return redirect(url_for('user_accounts.login'))

    else:
        # Form submission failed validation
        # Print validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in field '{field}': {error}")
                print(f"Error in field '{field}': {error}")
        return render_template('accounts/register.html', title='Register', form=form)

@bp.route('/user')
@bp.route('/user/')
@login_required
def user_page():
    # Retrieve the user's comments from the database
    user_comments = blog_comments.query.filter_by(user_id=current_user.id).all()
    sorted_user_comments = sorted(user_comments, key=attrgetter('post.title'))

    context = {
        'user_comments':sorted_user_comments,
        'current_user_username': current_user.username,
    }

    return render_template('accounts/user_page.html', **context)

@bp.route('/user/change_profile_picture', methods=['GET', 'POST'])
def change_profile_picture():
    if not current_user.is_authenticated:
        return redirect(url_for('user_accounts.user_page'))

    form = SubmitPictureForm()

    try:
        if form.validate_on_submit():
            if form.pic_file.data:
                #current user's username for the filename
                filename = secure_filename(current_user.username + '.' + form.pic_file.data.filename.rsplit('.', 1)[1].lower())
                
                
                input_path = config.basedir + '/app/static/img/user_pics/' + filename
                form.pic_file.data.save(input_path)
                #output_path = '/home/flambuth/new_fred/app/static/img/user_pics/

                resize_image(input_path)
                #current_user.profile_picture = output_path
                #flash('Profile picture updated successfully!')

                return redirect(url_for('user_accounts.user_page'))

    except RequestEntityTooLarge:
        # Handle file size error
        error_message = 'File size is too large. Please choose a smaller file.'
        return render_template('error_page.html', error_message=error_message)

    return render_template('accounts/change_profile_picture.html', title='Change Profile Picture', form=form)

@bp.route('/user_activity')
@login_required
def comment_activity():
    # Retrieve the user's comments from the database
    #user_comments = blog_comments.query.all()
    #last_five_comments = user_comments[::-1][:5]
    page = request.args.get('page', 1, type=int)
    per_page = 5
    comments = blog_comments.query.order_by(blog_comments.comment_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    context = {
        'user_comments':comments,
    }

    return render_template('accounts/all_users_comments.html', **context)

@bp.route('/users_page')
def all_users_page():
    stats = user_accounts.all_users_stats()

    context = {
        'user_stats':stats,
    }
    return render_template('accounts/all_users_showcase.html', **context)



'''
@bp.route('/spot_suc2')
def success2():

    # Retrieve access token from session or database
    access_token = session.get('access_token')

    if not access_token:
        # Handle case where access token is not available
        return redirect('/spotify_login')

    # Initialize Spotipy with the obtained access token
    sp = spotipy.Spotify(auth=access_token)

    # Example: Get user's saved tracks
    results = sp.current_user_saved_tracks()
    
    # Process the data and render a page with the user's saved tracks
    return f"User's saved tracks: {results}"
'''