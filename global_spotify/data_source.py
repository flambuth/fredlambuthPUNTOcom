import polars as pl
import json
import sqlite3
from datetime import date, timedelta

basedir = '/home/flambuth/fredlambuthPUNTOcom'

class UNIVERSAL_TOP_SPOTIFY_SONGS:
    def __init__(
            self,
            csv_location
            ) -> None:
        self.csv_location = csv_location
        self.lazy_df = pl.scan_csv(self.csv_location)
        self.first_date = self.scan_csv_date_endpoints(self.lazy_df)[0]
        self.last_date = self.scan_csv_date_endpoints(self.lazy_df)[1]

        self.country_codes = self.lazy_df.select('country').unique().collect().to_series().to_list()
        if '' in self.country_codes:
            self.country_codes.remove('')

    @staticmethod
    def add_inverted_rank_column(lazy_df):
        '''
        Adds a column that can be used for finding highest ranking artists
        '''
        df = lazy_df.with_columns(
            (50 + 1 - pl.col('daily_rank')).alias('inverted_rank')
        )
        return df

    @staticmethod
    def spotify_ids_in_df(lazy_df):
        '''
        Returns a list of unique strings found in the 'spotify_id' of the parameter lazy_df
        '''
        spotify_ids = lazy_df.select('spotify_id').unique().collect().to_series().to_list()
        return spotify_ids

    @staticmethod
    def scan_csv_date_endpoints(lazy_df):
        '''
        Scans the the expected location for CSV from Kaggle
        Returns the string date for the earliest and latest date of the CSV
        '''

        date_column = 'snapshot_date'
        lazy_min_date = lazy_df.select(pl.col(date_column).min().alias('min_date'))
        lazy_max_date = lazy_df.select(pl.col(date_column).max().alias('max_date'))
        
        min_date_df = lazy_min_date.collect()
        max_date_df = lazy_max_date.collect()

        # Extract the min and max date values
        min_date = min_date_df['min_date'][0]
        max_date = max_date_df['max_date'][0]
        return min_date, max_date

    @staticmethod
    def single_day_charts(
            lazy_df,
            chart_date
        ):
        '''
        Returns the recrods of one single days.
        '''
        
        one_day_lazy_frame = lazy_df.filter(
            pl.col('snapshot_date') == chart_date
        )
        return one_day_lazy_frame
    
    @staticmethod
    def last_90_days(lazy_df):
        '''
        Limits lazy df to the last 90 days
        '''
        ninety_days_delta = timedelta(days=90)
        date_obj_90_ago = date.today()-ninety_days_delta
        date_string = date_obj_90_ago.strftime(
            "%Y-%m-%d"
        )
        ninety_day_lazy_frame = lazy_df.filter(
            pl.col('snapshot_date') > date_string
        )
        return ninety_day_lazy_frame
    

    @staticmethod
    def older_hits(lazy_df, n=10):
        '''
        Returns the ten oldest tracks in the lazy_df
        '''
        df_unique = lazy_df.unique(subset=['spotify_id'], maintain_order=True)
        df_oldest = df_unique.sort('album_release_date').head(n)
        return df_oldest


    @staticmethod
    def split_artist_column(
            lazy_df
    ):
        '''
        Returns the lazy_df with a primary_artist and a featured_artists column, made from splitting
        the artists column
        '''
        df_split = lazy_df.with_columns(
            [pl.col("artists").str.split(",").alias("artists_list")]
        )
        df_prim_art = df_split.with_columns(
            [pl.col("artists_list").list.get(0).cast(pl.Utf8).alias('primary_artist')]
        )
        #df_feat_art = df_prim_art.with_columns(
        #    [pl.col("artists_list").list.slice(1).alias('featured_artists')]
        #)
        return df_prim_art.drop('artists_list')

    ###################
    # GROUPBY PRIMARY_ARTISTS
    @staticmethod
    def artist_appearance_count(lazy_df):
        '''
        Returns 2-col dataframe of artist appearances in the primary_artist column
        USE split_artist_column before this method
        '''
        df_counts = lazy_df.group_by(['primary_artist','country']).agg(
            pl.len().alias('appearances')
        ).sort('appearances', descending=True)
        return df_counts

    
    @staticmethod
    def artist_rank_percentage(lazy_df):
        '''
        Returns 2-col dataframe of the total rank percentage of the primary_artist column.
        USE split_artist_column before this method.
        '''
        # Step 1: Calculate the total rank for each artist
        df_counts = lazy_df.group_by(['primary_artist','country']).agg(
            pl.col('inverted_rank').sum().alias('total_rank')
        )
        
        # Step 2: Calculate the total rank sum across all artists
        total_rank_sum = df_counts.select(pl.col('total_rank').sum()).collect()[0, 0]

        # Step 3: Calculate the percentage for each artist
        df_percentages = df_counts.with_columns(
            ((pl.col('total_rank') / total_rank_sum) * 100).alias('rank_percentage')
        ).sort(['country', 'rank_percentage'], descending=[False, True])

        return df_percentages


    @staticmethod
    def artist_song_count(lazy_df):
        '''
        Returns 2-col dataframe of the unique song count of the primary_artist column
        USE split_artist_column before this method
        '''
        artist_song_counts = lazy_df.group_by('primary_artist').agg(
            pl.col('spotify_id').n_unique().alias('# of Songs')
        ).sort('# of Songs', descending=True)
        return artist_song_counts


class GLOBAL_SPOTIFY_DATABASE:
    '''
    Object that will hold the output of a daily ETL job that finds data about each country's
    daily top 10 tracks and artists
    '''
    def __init__(self, db_name) -> None:
        self.db_path = f'/home/flambuth/fredlambuthPUNTOcom/data/{db_name}.db'
        self.db_uri = "sqlite:///" + self.db_path
        self.conn = sqlite3.connect(self.db_path)

        with open('/home/flambuth/fredlambuthPUNTOcom/global_spotify/country_codes.json', 'r') as file:
            self.country_codes = json.load(file)