import sqlite3
import json
import polars as pl

from data_source import UNIVERSAL_TOP_SPOTIFY_SONGS

class COUNTRY_TOP_SPOTIFY_SONGS(UNIVERSAL_TOP_SPOTIFY_SONGS):
    '''
    Filtered down to one country. Enriches self.lazy_df with more columns
    '''
    def __init__(self, csv_location, country_code):
        super().__init__(csv_location)  
        self.country_code = country_code
        
        # Apply the filter to the LazyFrame for the specific country
        self.lazy_df = self.lazy_df.filter(
            pl.col('country') == self.country_code
        )

        # Apply the split_artist_column and add_inverted_rank_column transformations
        self.lazy_df = self.split_artist_column(self.lazy_df)
        self.lazy_df = self.add_inverted_rank_column(self.lazy_df)


    def add_country_column(self, lazy_df):
        '''
        Appends country to a polars dataframe
        '''
        df_with_country = lazy_df.with_columns(
            country=pl.lit(self.country_code)
        )
        return df_with_country
    
    def today_top10_track_history(self):
        '''
        Also resorts the history to match the sort order of the todays_top10_tracks

        '''
        df1 = self.todays_top10_tracks()
        
        top_10_spot_ids = df1.select('spotify_id').unique().collect()
        track_history = self.lazy_df.filter(
            pl.col('spotify_id').is_in(top_10_spot_ids)
        )
        
        # Creates the sort order for track_history from the latest daily top10 tracks
        spotify_order = df1.collect()['spotify_id'].to_list()
        spotify_order_dict = {spotify_id: index for index, spotify_id in enumerate(spotify_order)}

        df2 = track_history.with_columns(
            top10_sort_order=pl.col('spotify_id').replace(spotify_order_dict)
        )

        # sorts on the latest top10
        track_history_df = df2.sort('top10_sort_order')
        return track_history_df.drop('top10_sort_order')
    

    # 1 Artist DFs
    def todays_most_ranked_artists(self, n=10):
        '''
        Using the 
        '''
        art_df = self.artist_rank_percentage(self.lazy_df).head(n)
        arts = art_df.select('primary_artist').collect()

        art_song_count_df = self.artist_song_count(self.lazy_df)
        df = art_song_count_df.filter(
            pl.col('primary_artist').is_in(arts)
        )

        joined_df = art_df.join(df, on='primary_artist', how='inner')

        with_date_df = joined_df.with_columns(
            chart_date=pl.lit(self.last_date)
        )
        return with_date_df.sort('total_rank', descending=True)
    
class COUNTRY_TOP_SPOTIFY_SONGS_WITH_STATS(COUNTRY_TOP_SPOTIFY_SONGS):
    '''
    A child class that automatically calculates and stores three additional DataFrames:
    - today's top 10 tracks
    - today's top 10 track history
    - today's most ranked artists with song counts
    The DataFrame will only include data from the last 90 days.
    '''
    def __init__(self, csv_location, country_code):
        # Call the parent class constructor
        super().__init__(csv_location, country_code)

        # Truncates to the last 90 days
        self.lazy_df = self.last_90_days(self.lazy_df)
        self.first_date = self.scan_csv_date_endpoints(self.lazy_df)[0]

        # Track History goes back 90 days
        self.top_10_tracks = self.add_country_column(self.todays_top10_tracks()).collect()
        self.top_10_track_history = self.add_country_column(self.today_top10_track_history()).collect()
        self.top_10_artists = self.add_country_column(self.todays_most_ranked_artists()).collect()

        self.oldest_10 = self.add_country_column(self.older_hits(self.lazy_df)).collect()


    def write_to_database(
        self, 
        polars_df,
        db_table,
        ):
        db_obj = GLOBAL_SPOTIFY_DATABASE('global_TEST_auto_noGC')
        polars_df.write_database(
            db_table,
            connection=db_obj.db_uri,
            if_table_exists='append'
        )

        print(f'Written to database at {db_obj.db_path} for {self.country_code}')


def transform_csv_to_sqlite():
    csv_loc = '/home/flambuth/fredlambuthPUNTOcom/data/universal_top_spotify_songs.csv'
    db_name = 'global_TEST_auto'

    glob = GLOBAL_SPOTIFY_DATABASE(db_name)
    for country_code in glob.country_codes.keys():
        
        # Instantiate the country object
        country_obj = COUNTRY_TOP_SPOTIFY_SONGS_WITH_STATS(csv_loc, country_code)

        # Define table names
        table_names = [
            'top_10_songs_today',
            'top_10_song_data',
            'top_10_artists',
            'oldest_10_songs'
        ]

        # Write dataframes to the database
        country_obj.write_to_database(country_obj.top_10_tracks, table_names[0])
        country_obj.write_to_database(country_obj.top_10_track_history, table_names[1])
        country_obj.write_to_database(country_obj.top_10_artists, table_names[2])
        country_obj.write_to_database(country_obj.oldest_10, table_names[3])

        # Explicitly delete the country_obj and free memory
        # del country_obj
        # gc.collect()

if __name__ == '__main__':
    transform_csv_to_sqlite()
