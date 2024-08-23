import sqlite3
#from app.utils import push_app_context
#from app.models.charts import recently_played
import pandas as pd
import config


def make_archive_csv(archive_df):
    
    archive_df['track_id'] = archive_df.song_link.str[-22:]

    url_prefix = "https://i.scdn.co/image/"
    archive_df['image_code'] = archive_df.image.str.split(
        url_prefix,
        n=1,
        expand=True,
    )[1]

    archive_cols = [
        'last_played',
        'art_name', 
        'song_name',
        'track_id',
        'image_code'
    ]

    return archive_df[archive_cols]

def current_rps_not_in_archive(
        df_current,
        df_archive,
):
    missing_rps = df_current[ 
        ~df_current.last_played.isin(df_archive.last_played)
    ]
    return missing_rps


def first_rp_archive_entry():
    # An archive version of fredlambuth.db
    conn_archive = sqlite3.connect(config.basedir + '/data/' + config.archive_database)
    query = '''SELECT * FROM recently_played'''
    df_rp_archive = pd.read_sql(
        query,
        conn_archive
    )
    archive_df = make_archive_csv(df_rp_archive)

    # Current RP data
    conn_current = sqlite3.connect(config.basedir + '/data/' + config.database)
    df_rp_current = pd.read_sql(
        query,
        conn_current
    )

    missing_df = current_rps_not_in_archive(
        df_rp_current,
        df_rp_archive
    )
    archived_missing_df = make_archive_csv(missing_df)
    #in_current_not_in_archive['track_id'] = in_current_not_in_archive.song_link.str[-22:]

    archive_union = pd.concat(
        [archive_df,
        archived_missing_df],
        axis=0,
    )

    archive_union.to_csv(config.basedir + '/data/archives/recently_played.csv.gz', index=False, compression='gzip')


