import polars as pl
from datetime import date, timedelta

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
        df_feat_art = df_prim_art.with_columns(
            [pl.col("artists_list").list.slice(1).alias('featured_artists')]
        )
        return df_feat_art

    ###################
    # GROUPBY PRIMARY_ARTISTS
    @staticmethod
    def artist_appearance_count(lazy_df):
        '''
        Returns 2-col dataframe of artist appearances in the primary_artist column
        USE split_artist_column before this method
        '''
        df_counts = lazy_df.group_by('primary_artist').agg(
            pl.len().alias('appearances')
        ).sort('appearances', descending=True)
        return df_counts
    
    @staticmethod
    def artist_rank_sum(lazy_df):
        '''
        Returns 2-col dataframe of the total rank of the primary_artist column
        USE split_artist_column before this method
        '''
        df_counts = lazy_df.group_by('primary_artist').agg(
            pl.col('inverted_rank').sum().alias('total_rank')
        ).sort('total_rank', descending=True)
        return df_counts
    
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


    # Track Stats
    def todays_top10_tracks(self, n=10):
        first_day_chart = self.single_day_charts(
            self.lazy_df,
            self.last_date)
        return first_day_chart.head(n)
    
    def today_top10_track_history(self):
        df = self.todays_top10_tracks()
        top_10_spot_ids = df.select('spotify_id').unique().collect()

        track_history = self.lazy_df.filter(
            pl.col('spotify_id').is_in(top_10_spot_ids)
        )
        return track_history
    

    # Artist Stats
    def todays_most_ranked_artists(self, n=10):
        art_df = self.artist_rank_sum(self.lazy_df).head(n)
        arts = art_df.select('primary_artist').collect()

        art_song_count_df = self.artist_song_count(self.lazy_df)
        df = art_song_count_df.filter(
            pl.col('primary_artist').is_in(arts)
        )

        joined_df = art_df.join(df, on='primary_artist', how='inner')
        return joined_df.sort('total_rank', descending=True)