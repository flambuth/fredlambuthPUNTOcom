import sqlite3
import pandas as pd
import config
from scripts import rp_archives

class RP_Backend:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.basedir + '/data/' + config.database

    def _create_connection(self):
        """Creates and returns a new database connection."""
        return sqlite3.connect(self.db_path)

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

if __name__ == '__main__':
    RP_Backend().recently_played_shuffle()