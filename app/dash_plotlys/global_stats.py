from collections import Counter
import pandas as pd

from app.dash_plotlys.plotly_figures import songs_line_chart, artists_hbar_chart
import json
import sqlite3
import os

from config import basedir

country_codes_json = basedir + "/global_spotify/country_codes.json"
with open(country_codes_json, "r") as json_file:
    country_codes = json.load(json_file)
#################################
#data processing of the universal_top_spotify_songs.csv

def country_dash_dfs(country):
    conn = sqlite3.connect('data/global.db')
    tables = [
    'top_10_artists',
    'top_10_song_data',
    'top_10_songs_today'
]
    queries = [f"SELECT * from {table} where country_string='{country}';" for table in tables]
    
    df_artists = pd.read_sql(queries[0],conn)
    
    #some songs feature too many artists and it warps the legend of the 
    #plotly figure that is fed with this dataframe
    df_song_data = pd.read_sql(queries[1],conn)
    max_length = 100
    df_song_data['artists'] = df_song_data['artists'].str.slice(0, max_length)
    
    df_songs_today = pd.read_sql(queries[2],conn)
    return df_artists, df_song_data, df_songs_today

class Country_Dash_Components:
    def __init__(self, country_string):
        self.country = country_string
        self.df_top10_artists, self.df_top10_songs_data, self.df_top10_songs_today = country_dash_dfs(country_string)
        self.fig_top10_artists = artists_hbar_chart(self.df_top10_artists)
        self.fig_top10_song = songs_line_chart(self.df_top10_songs_data)
