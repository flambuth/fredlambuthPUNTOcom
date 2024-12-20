import polars as pl
import pandas as pd
import config

# current_rp_db = config.basedir + '/data/' + config.database
# archive_db = config.basedir + '/data/' + config.archive_database

rp_archive_csv = config.basedir + '/data/archives/recently_played.csv'

class RP_Archive_CSV:
    def __init__(self, csv_path=rp_archive_csv):
        self.csv_path = csv_path
        #self.df = self.load_csv()
        self.last_date = self.get_last_date_in_csv()

    def load_csv(self):
        return pd.read_csv(self.csv_path)
    
    def get_last_date_in_csv(self):
        with open(self.csv_path, 'rb') as f:
            f.seek(-2, 2)
            while f.read(1) != b'\n':
                f.seek(-2, 1)
            last_line = f.readline().decode()
        return last_line[:10]

    def filter_new_records(self, new_df):
        return new_df[new_df['last_played'] > self.last_date]


    def format_archive_df(self, df:pd.DataFrame) -> pd.DataFrame:
        '''
        Changes a rp dataframe to one that matches the archive CSV's schema
        '''
        df['track_id'] = df['song_link'].str[-22:]
        df['image_code'] = df['image'].str.split("https://i.scdn.co/image/", expand=True)[1]
        return df[['last_played', 'art_name', 'song_name', 'track_id', 'image_code']]

    def append_to_csv(self, df:pd.DataFrame) -> None:
        '''
        Accepts a pandas df formatted for the archive CSV,
        appends this df to the csv
        '''
        # Assert that all new records have dates later than the last date in the archive
        assert df['last_played'].min() > self.last_date, "Attempting to append data older than the latest date in the archive."

        df.to_csv(self.csv_path, mode='a', header=False, index=False)

    def archive_new_records(self, new_df):
        new_records = self.filter_new_records(new_df)
        formatted_df = self.format_archive_df(new_records)
        self.append_to_csv(formatted_df)


def fix_archive_csv_datetime():
    big_lazy = (
        pl.scan_csv(f"data/archives/recently_played.csv")
    )
    filtered_lf = big_lazy.filter(pl.col("last_played").str.len_chars() >= 19)
    lf_with_datetime = filtered_lf.with_columns(
        pl.col("last_played").str.strptime(pl.Datetime, format="%+", strict=False).alias("parsed_datetime")
    )

    easy_time = lf_with_datetime.filter(
        ~pl.col('parsed_datetime').is_null()
    )
    bad_time = lf_with_datetime.filter(
        pl.col('parsed_datetime').is_null()
    )
    bad_time_filtered_short = bad_time.filter(
        pl.col("last_played").str.len_chars() == 19  # Strings SHORTER than 19 characters have milliseconds
    )
    bad_time_filtered_long = bad_time.filter(
        pl.col("last_played").str.len_chars() > 19  # Strings longer than 19 characters have milliseconds
    )


    lf_easy = easy_time.with_columns(
        pl.col("last_played").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%.3fZ").alias('real_dt')
    ).with_columns(
        pl.col('real_dt').dt.truncate('1s').cast(pl.Datetime("ms"))  # Truncate and cast to milliseconds
    )

    lf_bad_short = bad_time_filtered_short.with_columns(
        pl.col("last_played").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S").alias('real_dt')
    ).with_columns(
        pl.col('real_dt').dt.truncate('1s').cast(pl.Datetime("ms"))  # Truncate and cast to milliseconds
    )

    lf_bad_long = bad_time_filtered_long.with_columns(
        pl.col("last_played").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S%.6f").alias('real_dt')
    ).with_columns(
        pl.col('real_dt').dt.truncate('1s').cast(pl.Datetime("ms"))  # Truncate and cast to milliseconds
    )
    lf_union = pl.concat([lf_easy, lf_bad_short, lf_bad_long], how="vertical")
    lf_switch = lf_union.drop('last_played', 'parsed_datetime')
    return lf_switch