import polars as pl
from config import basedir

def csv_lazy_df():
    csv_location = basedir + '/' + 'data/universal_top_spotify_songs.csv'
    lazy_df = pl.scan_csv(csv_location)
    return lazy_df

def scan_csv_date_endpoints():
    '''
    Scans the the expected location for the most current CSV from Kaggle
    Returns the string date for the earliest and latest date of the CSV
    '''
    lazy_df = csv_lazy_df()

    date_column = 'snapshot_date'
    lazy_min_date = lazy_df.select(pl.col(date_column).min().alias('min_date'))
    lazy_max_date = lazy_df.select(pl.col(date_column).max().alias('max_date'))
    
    min_date_df = lazy_min_date.collect()
    max_date_df = lazy_max_date.collect()

    # Extract the min and max date values
    min_date = min_date_df['min_date'][0]
    max_date = max_date_df['max_date'][0]
    
    return min_date, max_date


def first_and_last_day_charts():
    
    lazy_df = csv_lazy_df()
    
    first_date, last_date = scan_csv_date_endpoints()
    
    first_day_df = lazy_df.filter(
        pl.col('snapshot_date') == first_date
    ).collect()
    last_day_df = lazy_df.filter(
        pl.col('snapshot_date') == last_date
    ).collect()
    return first_day_df, last_day_df