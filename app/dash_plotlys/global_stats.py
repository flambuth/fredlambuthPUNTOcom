import pandas as pd
from app.dash_plotlys.plotly_figures import songs_line_chart
import sqlite3


def country_todays_tracks_stats(
        country_code,
        database='/home/flambuth/fredlambuthPUNTOcom/data/global.db'
        ):
    conn = sqlite3.connect(database)
    tables = [
    'top_10_artists',
    'top_10_song_data',
    'top_10_songs_today',
    'oldest_10_songs'
    ]
    queries = [f"SELECT * from {table} where country='{country_code}';" for table in tables]
    
    df_artists = pd.read_sql(queries[0],conn)
    df_song_data = pd.read_sql(queries[1],conn)
    df_songs_today = pd.read_sql(queries[2],conn)
    df_oldest_10_today = pd.read_sql(queries[3],conn)

    return df_artists, df_song_data, df_songs_today, df_oldest_10_today


class Country_Dash_Components:
    def __init__(self, country_code, database):
        self.country = country_code
        self.df_top10_artists, self.df_top10_songs_data, self.df_top10_songs_today, self.df_ten_oldest = country_todays_tracks_stats(
            country_code,
            database=database
        )
