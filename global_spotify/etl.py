import json
import pandas as pd
import sqlite3
from collections import Counter

def country_codes_map():
    '''
    
    '''
    country_codes_json = "/home/flambuth/fredlambuthPUNTOcom/global_spotify/country_codes.json"
    with open(country_codes_json, "r") as json_file:
        country_codes = json.load(json_file)
    return country_codes

def cleaned_df(
        csv_name='/home/flambuth/fredlambuthPUNTOcom/universal_top_spotify_songs.csv',
        chunk_size=13000
        ):
    '''
    csv_name = 'universal_top_spotify_songs.csv'
    '''
    big_df = pd.read_csv(csv_name).dropna()
    big_df['country_string'] = big_df.country.map(country_codes_map())
    return big_df

def cleaned_df_country(country_code):
    '''
    csv_name = 'universal_top_spotify_songs.csv'
    '''
    big_df = cleaned_df()
    country_df = big_df[ big_df.country == country_code]
    return country_df

class Country_Stats:
    def __init__(
        self,
        country_code
        ):
        
        self.df = cleaned_df_country(country_code) 

    def filter_spotify_ids(self, spotify_ids, df):
        filtered_df = df[df.spotify_id.isin(spotify_ids)]
        return filtered_df

    def top_n_names_in_df(self,n=10):
        
        '''
        Groups all the names and sums the popularity for that name.
        Returns a three column dataframe:
        name: song_name,
        artists: single artist string or CSV of artists
        popularity: sum values of popularity across all days in data
        '''
        top_names = self.df.groupby(['spotify_id','name', 'artists']).sum('popularity').sort_values(by='popularity', ascending=False)
        df_top_names = top_names.reset_index()
        return df_top_names[['spotify_id','name', 'artists', 'popularity']].head(n)
    
    def todays_top10(self):
        '''
        Returns the top 10 songs for today of the dataframe. 
        If you give it a dataframe for one region, it will return a 10
        row dataframe
        Returns a dataframe with 10 rows for each value in the 'country' column
        '''
        latest_date = max(self.df.snapshot_date)
        today = self.df[self.df.snapshot_date == latest_date]
        today_top10 = today[today.daily_rank < 11]
        return today_top10[['daily_rank', 'name', 'artists']]
    
    def slice_artists_names(self):
        '''
        Returns a tuple
        0 is the art_names in the primary position
        1 is the art_names that came after the primary position in one song
        '''
        primaries = []
        secondaries = []

        for entry in self.df.artists:
            if ',' in entry:
                names = [name.strip() for name in entry.split(',')]
                primaries.append(names[0])
                secondaries.extend(names[1:])
            else:
                primaries.append(entry)

        return primaries, secondaries

    def get_sorted_artists(self):
        return sorted(list(set(self.slice_artists_names()[0])))

    def get_sorted_featured_artists(self):
        return sorted(list(set(self.slice_artists_names()[1])))

    def count_artist_unique_songs(self, artist_name):
        song_count = self.df[self.df.artists.str.contains(artist_name)].name.nunique()
        return song_count

    def get_top_n_artists(self, n=10):
        prims, secs = self.slice_artists_names()
        name_counter = Counter(prims)
        sec_name_counter = Counter(secs)
        doubler = {i[0]: i[1] for i in name_counter.items()}
        name_counter.update(doubler)

        secs_dict = {i[0]: i[1] for i in sec_name_counter.items()}
        name_counter.update(secs_dict)

        tuples = name_counter.most_common(n)

        result_list = [(artist, count, self.count_artist_unique_songs(artist)) for artist, count in tuples]

        cols = ['artist','appearances','unique_songs']
        df = pd.DataFrame(result_list, columns=cols)
        return df
    
class Country_Dataframes(Country_Stats):

    def __init__(self, country_code):
        super().__init__(country_code)

        self.df_top_10_artists = self.get_top_n_artists()

        self.df_today_top10 = self.todays_top10()

        self.df_top_10_songs = self.top_n_names_in_df()
        self.df_top_10_songs_data = self.filter_spotify_ids(
            self.df_top_10_songs.spotify_id, self.df)[[
                'daily_rank',
                'name', 'artists',
                'snapshot_date',
            ]]

    def write_dfs_to_db(self):
        conn = sqlite3.connect('global.db')
        self.df_top_10_data.to_sql('top_10_song_data', conn, index=False, if_exists='replace')
        self.df_today_top10.to_sql('top_10_songs_today', conn, index=False, if_exists='replace')
        self.df_top_10_songs.to_sql('top_10_artists', conn, index=False, if_exists='replace')

def write_all_countries_to_db():
    '''
    Iterates alphabetically through the country_codes dictionary. At each iteration:
        three dataframes are made of:
            10 artists with most chart data,
            10 top songs today,
            10 songs with largest total chart history
        each dataframe is written to a table in a 'global.db' SQLITE file in the current
        directory
    '''
    codes = country_codes_map().keys()
    for country_code in codes:
        Country_Dataframes.write_dfs_to_db(country_code)

#write_all_countries_to_db()

#print('Snide remark for success!')