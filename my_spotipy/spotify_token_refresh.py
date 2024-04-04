import json
import config
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import os

def refresh_token_for_user(spotify_username):
    # Load tokens from JSON file
    #tokens_directory = os.path.join(os.getcwd(),'my_spotipy', 'user_tokens')

    # Construct the filename for the JSON file based on the username
    json_filename = config.basedir + f'/my_spotipy/user_tokens/cache-{spotify_username}.json'

    with open(json_filename, 'r') as f:
        tokens = json.load(f)

    cache_path = os.path.join(config.basedir, 'my_spotipy', 'user_tokens', '.cache')
    cache_handler = CacheFileHandler(cache_path=cache_path, username=spotify_username)

    # Initialize Spotipy OAuth object with client ID, client secret, and refresh token
    sp_oauth = SpotifyOAuth(
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=config.SPOTIPY_REDIRECT_URI,
        scope=config.scope,
        cache_handler=cache_handler,
        #refresh_token=tokens['refresh_token']
    )

    # Attempt to refresh access token
    new_token_info = sp_oauth.refresh_access_token(tokens['refresh_token'])

    # Check if token refresh was successful
    if new_token_info:
        # Update access token with new token
        tokens['access_token'] = new_token_info['access_token']

        # Save updated tokens back to JSON file
        with open(json_filename, 'w') as f:
            json.dump(tokens, f)

        return True
    else:
        print("Token not refreshed")