from my_spotipy import spotify_daily
from app.models.charts import daily_artists, daily_tracks
from app.utils import push_app_context
from spotify_token_refresh import refresh_token_for_user

if __name__ == '__main__':
    refresh_token_for_user('lambuth')

    spotify_daily.DailyCharts(
        daily_tracks,
        push_app_context(),
        'lambuth'
    ).add_daily_to_db()
    spotify_daily.DailyCharts(
        daily_artists,
        push_app_context(),
        'lambuth'
    ).add_daily_to_db()
    