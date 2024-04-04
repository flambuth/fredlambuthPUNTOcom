import json
import os
import config
from spotipy.oauth2 import SpotifyOAuth

def refresh_token_for_user(spotify_username):
    # Load tokens from JSON file
    tokens_directory = os.path.join(os.getcwd(), 'my_spotipy', 'user_tokens')

    # Construct the filename for the JSON file based on the username
    json_filename = os.path.join(tokens_directory, f'cache-{spotify_username}.json')

    with open(json_filename, 'r') as f:
        tokens = json.load(f)

    # Initialize Spotipy OAuth object with client ID, client secret, and refresh token
    sp_oauth = SpotifyOAuth(
        client_id=config.SPOTIPY_CLIENT_ID,
        client_secret=config.SPOTIPY_CLIENT_SECRET,
        redirect_uri=config.SPOTIPY_REDIRECT_URI,
        scope=config.scope,
        #refresh_token=tokens['refresh_token']
    )

    # Attempt to refresh access token
    new_token_info = sp_oauth.refresh_access_token(tokens['refresh_token'])

    # Check if token refresh was successful
    if new_token_info:
        # Update access token with new token
        tokens['access_token'] = new_token_info['access_token']

        # Save updated tokens back to JSON file
        with open(f'cache-{spotify_username}.json', 'w') as f:
            json.dump(tokens, f)

        # Use the new access token to make API requests
        #sp = spotipy.Spotify(auth=tokens['access_token'])
        # Now you can use sp to make authenticated requests

        # Example: Get user's currently playing track
        #results = sp.current_user_playing_track()
        #if results:
        #   print(f"User currently listening to: {results['item']['name']} by {results['item']['artists'][0]['name']} with my ADDIDAS")
        #else:
        #    print('no new song')
        return True
    else:
        print("Token not refreshed")