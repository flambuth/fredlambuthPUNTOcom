import sqlite3
import pandas as pd
import polars as pl

#import config
from scripts import rp_archives
from my_spotipy.spotify_catalog import ArtistCatalog, list_to_art_cat_obj

class RP_Backend:
    '''Methods that use the table used by the recently_played Flask model'''
    def __init__(self, db_path=None):
        #self.db_path = db_path or config.basedir + '/data/' + config.database
        # embarassing hardcoded path to the db. We should use global variables for this.
        self.db_path = db_path or '/home/flambuth/fredlambuthPUNTOcom/data/fred.db'

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

    def recently_played_shuffle(self, rp_archives_obj):
        '''
        Appends rp_records not found in the CSV.
        Truncates the rp model down to the last 100 days only if appending succeeds.
        '''
        archive_df = rp_archives_obj.load_csv()
        missing_in_archives = self.current_rps_not_in_archive(archive_df)
        formatted = rp_archives_obj.format_archive_df(missing_in_archives)
        
        success = rp_archives_obj.append_to_csv(formatted)  # Ensure this method returns True on success
        
        if success:
            self.truncate_rps_older_than_n_days(100)
        else:
            print("Append operation failed, truncation skipped.")

######## POLARS
# artcat and rp_archive
class ArtCat_Backend:
    def __init__(self, db_path):
        self.db_path = db_path
    #   artist_catalog model
    
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

    #######
    # rp_archives 
    def archive_rps_not_in_art_cat(self, rp_archive_obj):
        '''Returns a list of art names or ids found in the RP archives'''
        df_archive = rp_archive_obj.fix_archive_csv_datetime()
        
        archive_with_art_cat_col = df_archive.with_columns(
            pl.col('art_name').is_in(self.current_art_cat_polars().select('art_name')).alias('in_art_cat')
        )
        archive_not_in_art_cat = archive_with_art_cat_col.filter(
            pl.col('in_art_cat') == False
        )
        return archive_not_in_art_cat
    
    # artist appearances
    def mia_from_art_cat_groups(self, rp_archive_obj, threshold=25):
        '''
        Returns a Groupby polars lazyframe of the appearances and distinct songs for each art_name in
        the MIA from RP models dataframe.
        '''
        archive_not_in_art_cat = self.archive_rps_not_in_art_cat(rp_archive_obj)
        mia_in_archives_groups = archive_not_in_art_cat.group_by('art_name').agg(
            pl.len().alias('appearances'),
            pl.col('song_name').unique(),
            pl.col('song_name').n_unique().alias('distinct_songs')
        ).sort("appearances", descending=True)
        above_threshold = mia_in_archives_groups.filter(
            pl.col('appearances') > threshold
        )
        return above_threshold

    # song appearances
    def songs_missing_from_art_cat(self, rp_archive_obj, threshold=17):
        new_df = self.archive_rps_not_in_art_cat(rp_archive_obj)
        songs_not_in_track_cat = new_df.group_by('art_name','song_name', 'track_id').agg(
            pl.len().alias('appearances'),
        ).sort("appearances", descending=True)
        above_threshold = songs_not_in_track_cat.filter(
            pl.col('appearances') > threshold
        )
        return above_threshold

    def mia_list(self, rp_archive_obj, threshold=25):
        '''
        Uses rp_backen to compare rp_archives with the artist_catalog model
        
        returns list of names of artists that have song counts above threshold
        but are not found in the artist_catalog model
        '''
        lazy_df_of_mias = self.mia_from_art_cat_groups(rp_archive_obj, threshold)
        the_list = lazy_df_of_mias.select(pl.col("art_name")).collect().to_series().to_list()
        return the_list
    
    #####
    # SPOTIFY API Calls
    @staticmethod
    def art_names_to_ac_entries(art_name_list):
        '''
        Converts an art_name string to a art_cat object ready to be added to the model
        '''
        # maps spotify API calls to each art_name, making a list of JSONS
        the_list_of_spots = list(map(
            ArtistCatalog.art_name_to_art_cat,
            art_name_list
        ))
        almost_ready = [ArtistCatalog.static_new_entry(artist_data) for artist_data in the_list_of_spots]
        
        ready_for_adding = list(map(
            list_to_art_cat_obj,
            almost_ready
        ))
        
        return ready_for_adding
    
    # SPOTIFY API calls
    def mias_ready_for_catalog(self, rp_archive_obj, threshold=25):
        '''
        threshold is how many song appearances in rp_archives are needed
        to be declared MIA from the art_cat model
        
        Returns artist_catalog model objects that can be added via the artist_catalog.add_new_art_cat_to_db method
        '''
        # list of art_names found in rp_archives not found in the art_cat model
        the_list = self.mia_list(rp_archive_obj, threshold)
        # Maps Spotify API call >> List >>
        art_cat_entries = self.art_names_to_ac_entries(the_list)
        return art_cat_entries

if __name__ == '__main__':
    usal_csv_path = '/home/flambuth/fredlambuthPUNTOcom/data/archives/recently_played.csv'
    usual_db_path = '/home/flambuth/fredlambuthPUNTOcom/data/fred.db'
    archives_obj = rp_archives.RP_Archive_CSV(usal_csv_path)
    RP_Backend(usual_db_path).recently_played_shuffle(archives_obj)