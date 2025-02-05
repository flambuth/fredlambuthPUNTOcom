from datetime import date
from my_spotipy import spotify_daily
from app.models.charts import daily_artists, daily_tracks
from app.utils import push_app_context
from my_spotipy.spotify_token_refresh import refresh_token_for_user
from config import username

def daily_backup_check(daily_class):
    """
    Returns True if the latest date in the database is NOT equal to today's date.
    This means the update failed and needs to be retried.
    """
    today_date = date.today()
    latest_class_date = daily_class.get_latest_date()
    return latest_class_date != today_date

def backup_run(daily_class):
    """
    Checks if the latest date is missing today's data and reruns the update if necessary.
    """
    if daily_backup_check(daily_class):
        print(f"Backup run triggered for {daily_class.__name__}...")
        spotify_daily.DailyCharts(
            daily_class,
            push_app_context(),
            username
        ).add_daily_to_db()
    else:
        print(f"{daily_class.__name__} already up to date.")

def main():
    """
    Main execution function with redundancy checks.
    """
    try:
        # Refresh Spotify token before making API requests
        refresh_token_for_user(username)

        # Run the daily job for both models
        spotify_daily.DailyCharts(
            daily_tracks,
            push_app_context(),
            username
        ).add_daily_to_db()
        spotify_daily.DailyCharts(
            daily_artists,
            push_app_context(),
            username
        ).add_daily_to_db()

    except Exception as e:
        print(f"Error in primary execution: {e}")
        print("Checking if backup run is needed...")

        # If failure occurs, check if the backup run is needed
        backup_run(daily_tracks)
        backup_run(daily_artists)

if __name__ == '__main__':
    main()