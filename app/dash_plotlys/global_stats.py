from collections import Counter
import pandas as pd

from app.dash_plotlys.plotly_figures import songs_line_chart, artists_hbar_chart
import json
import sqlite3

# Load the dictionary from the JSON file
with open("country_codes.json", "r") as json_file:
    country_codes = json.load(json_file)

def cleaned_df(csv_name='universal_top_spotify_songs.csv'):
    '''
    csv_name = 'universal_top_spotify_songs.csv'
    '''

    big_df = pd.read_csv(csv_name).dropna()
    big_df['country_string'] = big_df.country.map(country_codes)
    return big_df

class Chart_Data:
    def __init__(self, df=None):
        if df is None:
            self.df = cleaned_df()
        else:
            self.df = df
        #iso_string of the latest date in the dataframe            
        self.latest_date = max(self.df.snapshot_date)

    def filter_country(self, country_string, df):
        '''
        Filters the dataframe down to a single country code
        '''
        return df[df.country_string == country_string]
    
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

class Country_Chart_Data(Chart_Data):
    '''
    Depends on that Country_String. The csv only has the country codes
    '''

    def __init__(self, country_string):
        super().__init__()  # df will be set using cleaned_df() from the parent class

        # Filter the data for the specific country
        self.country = country_string
        self.df = self.filter_country(country_string, self.df)

        # Compute top 10 songs for the country
        self.df_top_10_songs = self.top_n_names_in_df()
        self.df_top_10_data = self.filter_spotify_ids(
            self.df_top_10_songs.spotify_id, self.df)[[
                'daily_rank',
                'name', 'artists',
                'snapshot_date',
            ]]
        
        # Generate line chart for top 10 songs in the country
        self.fig_top10_song = songs_line_chart(self.df_top_10_data)

        # Compute today's top 10 songs for the country
        self.df_today_top10 = self.todays_top10()

        # Get sorted lists of artists and featured artists
        self.artists = self.get_sorted_artists()
        self.featured_artists = self.get_sorted_featured_artists()

        # Get top 10 artists for the country
        self.top_10_artists = self.get_top_n_artists()

        self.fig_top10_artists = artists_hbar_chart(self.top_10_artists)

class Country_Data(Chart_Data):
    '''
    Country's necessary data to display on the dashboard.
    '''

    def __init__(self, country_string):
        super().__init__()  # df will be set using cleaned_df() from the parent class

        # Filter the data for the specific country
        self.country = country_string
        self.df = self.filter_country(country_string, self.df)

        # Compute top 10 songs for the country
        self.df_top_10_songs = self.top_n_names_in_df()
        #filters the self.df down to just any row that has a spotify song_id in this country's top 10 songs
        self.df_top_10_data = self.filter_spotify_ids(
            self.df_top_10_songs.spotify_id, self.df)[[
                'daily_rank',
                'name', 'artists',
                'snapshot_date',
            ]]

        # Compute today's top 10 songs for the country
        self.df_today_top10 = self.todays_top10()


        # Get top 10 artists for the country
        self.df_top_10_artists = self.get_top_n_artists()

    def add_country_column(self):
        '''
        Add a 'country' column to all dataframes in the object.
        '''
        country_value = self.country

        # Add 'country' column to each dataframe
        self.df['country'] = country_value
        self.df_top_10_songs['country'] = country_value
        self.df_top_10_data['country'] = country_value
        self.df_today_top10['country'] = country_value
        self.df_top_10_artists['country'] = country_value


#################################
#data processing of the universal_top_spotify_songs.csv
def initiate_db(country_names, db='global.db'):
    conn = sqlite3.connect(db)

    # Initialize the first country
    first_country = country_names[0]
    first_obj = Country_Data(first_country)
    first_obj.add_country_column()
    
    # Insert data for the first country
    first_obj.df_top_10_artists.to_sql('top_10_artists', conn, index=False, if_exists='replace')
    first_obj.df_top_10_data.to_sql('top_10_song_data', conn, index=False, if_exists='replace')
    first_obj.df_today_top10.to_sql('top_10_songs_today', conn, index=False, if_exists='replace')

    # Append data for the remaining countries
    append_data_for_countries(country_names[1:], conn)

def append_data_for_countries(country_names, conn):
    for country in country_names:
        country_obj = Country_Data(country)
        country_obj.add_country_column()

        # Append data to the existing tables
        country_obj.df_top_10_artists.to_sql('top_10_artists', conn, index=False, if_exists='append')
        country_obj.df_top_10_data.to_sql('top_10_song_data', conn, index=False, if_exists='append')
        country_obj.df_today_top10.to_sql('top_10_songs_today', conn, index=False, if_exists='append')

def country_dash_dfs(country):
    conn = sqlite3.connect('global.db')
    tables = [
    'top_10_artists',
    'top_10_song_data',
    'top_10_songs_today'
]
    queries = [f"SELECT * from {table} where country='{country}';" for table in tables]
    
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
'''
class Country_Dash_Components:
    conn = sqlite3.connect('global.db')
    query = f"SELECT * from {table} where country='{test_country}';"
    def __init__(self, country_string):
        self.country = country_string
        self.df_top10_song_data 
        self.df_top10_songs_today
        self.df_top10_artists
'''
