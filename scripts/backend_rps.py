import sqlite3
import pandas as pd
import polars as pl
import config
from scripts import rp_archives

class RP_Backend:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.basedir + '/data/' + config.database

    def _create_connection(self):
        """Creates and returns a new database connection."""
        return sqlite3.connect(self.db_path)

    # PANDAS
    def fetch_current_rps_df(self) -> pd.DataFrame:
        """Fetches the recently played data from the SQLite database as a DataFrame."""
        query = "SELECT * FROM recently_played"
        with self._create_connection() as conn:
            df = pd.read_sql(query, conn)
        return df

    def rps_in_current_after_date(
            self, 
            archive_date: str) -> pd.DataFrame:
        """Returns records in the current dataframe after the given archive date."""
        df = self.fetch_current_rps_df()
        return df[df['last_played'] > archive_date]

    def current_rps_not_in_archive(
            self, 
            df_archive: pd.DataFrame) -> pd.DataFrame:
        """Finds records in the current dataframe that have not been archived."""
        df_current = self.fetch_current_rps_df()
        missing_rps = df_current[~df_current['last_played'].isin(df_archive['last_played'])]
        return missing_rps

    def truncate_rps_older_than_n_days(
            self, 
            n_days: int):
        """Deletes records older than the specified number of days from the database."""
        query = f"DELETE FROM recently_played WHERE last_played < DATE('now', '-{n_days} days')"
        with self._create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def recently_played_shuffle(self):
        '''
        Appends rp_records not found in the CSV.
        Truncates the rp model down to the last 100 days
        '''
        the_annals = rp_archives.RP_Archive_CSV()

        archive_df = the_annals.load_csv()
        missing_in_archives = self.current_rps_not_in_archive(archive_df)
        formatted = the_annals.format_archive_df(missing_in_archives)
        the_annals.append_to_csv(formatted)
        
        self.truncate_rps_older_than_n_days(100)
        
    # POLARS
    def current_art_cat_polars(self):
        '''
        With a given path to a fredlambuth.com db, returns a polars dataframe
        of the artist_catalog table where is_current=True
        '''
        db_uri = "sqlite:///" + self.db_path
        query = 'select * from artist_catalog;'
        art_cat_df = pl.read_database_uri(
            query=query,
            uri=db_uri
        )
        current_art_cat_df = art_cat_df.filter(
            pl.col('is_current') == True
        )
        return current_art_cat_df

    def archive_rps_not_in_art_cat(self):
        '''Returns a list of art names or ids found in the RP archives'''
        df_archive = rp_archives.fix_archive_csv_datetime()
        
        archive_with_art_cat_col = df_archive.with_columns(
            pl.col('art_name').is_in(self.current_art_cat_polars().select('art_name')).alias('in_art_cat')
        )
        archive_not_in_art_cat = archive_with_art_cat_col.filter(
            pl.col('in_art_cat') == False
        )
        return archive_not_in_art_cat
    
    def mia_from_art_cat_groups(self, threshold=20):
        '''
        Returns a Groupby polars lazyframe of the appearances and distinct songs for each art_name in
        the MIA from RP models dataframe.
        '''
        archive_not_in_art_cat = self.archive_rps_not_in_art_cat()
        mia_in_archives_groups = archive_not_in_art_cat.group_by('art_name').agg(
            pl.len().alias('appearances'),
            pl.col('song_name').unique(),
            pl.col('song_name').n_unique().alias('distinct_songs')
        ).sort("appearances", descending=True)
        above_threshold = mia_in_archives_groups.filter(
            pl.col('appearances') > threshold
        )
        return above_threshold

if __name__ == '__main__':
    usual_db_path = '/home/flambuth/fredlambuthPUNTOcom/data/fred.db'
    RP_Backend(usual_db_path).recently_played_shuffle()