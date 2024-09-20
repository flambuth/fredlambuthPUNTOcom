import polars as pl
from data_source import UNIVERSAL_TOP_SPOTIFY_SONGS, GLOBAL_SPOTIFY_DATABASE
import time

class UTSS_ETL_Tools(UNIVERSAL_TOP_SPOTIFY_SONGS):
    '''
    '''
    def __init__(self, csv_location):
        # Call the parent class constructor
        super().__init__(csv_location)

        # Truncates to the last 90 days
        self.lazy_df = self.add_inverted_rank_column(self.split_artist_column(
            self.last_90_days(
                self.lazy_df)
                )).filter(
                    pl.col('country') != ""
                )
        self.first_date = self.scan_csv_date_endpoints(self.lazy_df)[0]

    def todays_top10_tracks(self):
        '''
        Just the lastest top10. No history.
        '''
        first_day_chart = self.single_day_charts(
            self.lazy_df,
            self.last_date)
        today_10_only_df = first_day_chart.filter(
            pl.col('daily_rank')<11)
        return today_10_only_df
    
    def today_top10_history(self):
        '''
        I'm accidentally pulling in history for out of context for a country's daily top10
        '''
        spot_ids_w_country_df = UNIVERSAL_TOP_SPOTIFY_SONGS.spotify_ids_and_country_in_df(
            self.lazy_df
        )
        top10_history_df = self.lazy_df.join(
            spot_ids_w_country_df,
            on=['spotify_id','country'],
            how='inner'
        )

        return top10_history_df
    
    def today_oldest_10_tracks(self):
        df_olds = self.lazy_df.sort('snapshot_date').group_by('country').agg(
            pl.all().slice(0,10)
        ).explode(pl.exclude('country'))
        return df_olds
    
    def today_top10_artists_stats(self):
        '''
        Joins all stats about artists per country.
        '''
        df_app_count = self.artist_appearance_count(self.lazy_df)
        df_rank_pct = self.artist_rank_percentage(self.lazy_df)
        df_song_count = self.artist_song_count(self.lazy_df)

        df_merged = df_app_count.join(
            df_rank_pct, on=['primary_artist', 'country'], how='inner')
        
        df_final = df_merged.join(df_song_count, on='primary_artist', how='inner')
        return df_final
    

class UTSS_Load(UTSS_ETL_Tools):
    def __init__(self, csv_location, database):
        super().__init__(csv_location)
        self.db = database
        self.db_tables = [
            'top_10_songs_today',
            'top_10_song_data',
            'top_10_artists',
            'oldest_10_songs'
        ]

        self.top_10_track_today = self.todays_top10_tracks()
        self.top_10_track_history = self.today_top10_history()
        self.top_10_artists = self.today_top10_artists_stats()
        self.top_10_oldest = self.today_oldest_10_tracks()

    def load_dataframe_to_DB(
            self, 
            polars_df,
            db_table,
        ):
        db_obj = GLOBAL_SPOTIFY_DATABASE(self.db)
        polars_df.write_database(
            db_table,
            connection=db_obj.db_uri,
            if_table_exists='replace'
        )

        print('saved!')

    def transform_csv_to_sqlite(self):    
        # Write dataframes to the database
        self.load_dataframe_to_DB(self.top_10_track_today.collect(), self.db_tables[0])
        self.load_dataframe_to_DB(self.top_10_track_history.collect(), self.db_tables[1])
        self.load_dataframe_to_DB(self.top_10_artists.collect(), self.db_tables[2])
        self.load_dataframe_to_DB(self.top_10_oldest.collect(), self.db_tables[3])

        print(f'All Loaded into {self.db}')

if __name__ == '__main__':
    start_time = time.time()

    csv_loc = "/home/flambuth/fredlambuthPUNTOcom/data/universal_top_spotify_songs.csv"
    db_name = "global"
    UTSS_Load(
        csv_loc,
        db_name
    ).transform_csv_to_sqlite()

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")