# import sqlite3
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
