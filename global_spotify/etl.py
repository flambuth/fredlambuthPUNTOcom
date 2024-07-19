import json
import pandas as pd
import sqlite3
from collections import Counter
import gc

def country_codes_map():
    '''
    
    '''
    country_codes_json = "/home/flambuth/fredlambuthPUNTOcom/global_spotify/country_codes.json"
    with open(country_codes_json, "r") as json_file:
        country_codes = json.load(json_file)
    return country_codes

def cleaned_df(
        csv_name='/home/flambuth/fredlambuthPUNTOcom/data/universal_top_spotify_songs.csv',
        chunk_size=13000
        ):
    country_codes = country_codes_map()
    chunks = pd.read_csv(csv_name, chunksize=chunk_size)
    for chunk in chunks:
        chunk = chunk.dropna()
        chunk['country_string'] = chunk.country.map(country_codes)
        yield chunk

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
        self.country_code = country_code
        self.df = self._load_country_df()

    def _load_country_df(self):
        country_df_list = []
        for chunk in cleaned_df():
            country_chunk = chunk[chunk.country == self.country_code]
            country_df_list.append(country_chunk)
        return pd.concat(country_df_list)

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
        self.country_code = country_code
        self.country_string = country_codes_map().get(self.country_code)

        self.df_top_10_artists = self.get_top_n_artists()

        self.df_today_top10 = self.todays_top10()

        self.df_top_10_songs = self.top_n_names_in_df()
        self.df_top_10_songs_data = self.filter_spotify_ids(
            self.df_top_10_songs.spotify_id, self.df)[[
                'daily_rank',
                'name', 'artists',
                'snapshot_date',
            ]]

    def add_country_column(self):
        """
        Add the country code to the dataframes.
        """
        self.df_top_10_songs_data['country'] = self.country_code
        self.df_today_top10['country'] = self.country_code
        self.df_top_10_artists['country'] = self.country_code

        self.df_top_10_songs_data['country_string'] = self.country_string
        self.df_today_top10['country_string'] = self.country_string
        self.df_top_10_artists['country_string'] = self.country_string



    def write_dfs_to_db(self):
        conn = sqlite3.connect('data/global.db')
        try:
            self.df_top_10_songs_data.to_sql('top_10_song_data', conn, index=False, if_exists='append')
            self.df_today_top10.to_sql('top_10_songs_today', conn, index=False, if_exists='append')
            self.df_top_10_artists.to_sql('top_10_artists', conn, index=False, if_exists='append')

            # Debugging: Check the number of rows in each table after appending
            top_10_song_data_count = pd.read_sql_query("SELECT COUNT(*) FROM top_10_song_data", conn).iloc[0, 0]
            top_10_songs_today_count = pd.read_sql_query("SELECT COUNT(*) FROM top_10_songs_today", conn).iloc[0, 0]
            top_10_artists_count = pd.read_sql_query("SELECT COUNT(*) FROM top_10_artists", conn).iloc[0, 0]

            print(f"After appending for {self.country_code}:")
            print(f"top_10_song_data: {top_10_song_data_count} rows")
            print(f"top_10_songs_today: {top_10_songs_today_count} rows")
            print(f"top_10_artists: {top_10_artists_count} rows")
        finally:
            conn.close()

def write_all_countries_to_db():
    '''
    Drops existing tables so that each run's data is the only available in the
    database

    Iterates alphabetically through the country_codes dictionary. At each iteration:
        three dataframes are made of:
            10 artists with most chart data,
            10 top songs today,
            10 songs with largest total chart history
        each dataframe is written to a table in a 'data/global.db' SQLITE file in the current
        directory
    '''
    conn = sqlite3.connect('data/global.db')
    conn.execute("DROP TABLE IF EXISTS top_10_song_data")
    conn.execute("DROP TABLE IF EXISTS top_10_songs_today")
    conn.execute("DROP TABLE IF EXISTS top_10_artists")
    conn.close()

    codes = country_codes_map().keys()
    for country_code in codes:
        country_obj = Country_Dataframes(country_code)
        country_obj.add_country_column()
        country_obj.write_dfs_to_db()
        
        #give baCK memory
        del country_obj
        gc.collect()

if __name__ == '__main__':
    write_all_countries_to_db()