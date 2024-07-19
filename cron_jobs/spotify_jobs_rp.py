from my_spotipy import spotify_recently
from app.models.charts import recently_played
from app.utils import push_app_context
#from my_spotipy.spotify_token_refresh import refresh_token_for_user


if __name__ == '__main__':
    #refresh_token_for_user('lambuth')

    spotify_recently.CurrentlyPlaying(
    recently_played,
    push_app_context(),
    'lambuth',
    ).add_to_recently_played()

