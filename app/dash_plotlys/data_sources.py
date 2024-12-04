from app.models.catalogs import artist_catalog
from app.models.charts import daily_artists, daily_tracks, recently_played
from app import utils
from collections import Counter
import pandas as pd

class Chart_Year_Month_Stats:

    def __init__(self, year, month):
        #self.top_5_in_tracks = daily_tracks.hits_in_year_month(year, month)
        #self.top_5_names_in_tracks = [i[0] for i in self.top_5_in_tracks]

        #find the top5 artists names of the year-month set by the parameters
        self.top_5_in_arts = daily_artists.hits_in_year_month(year, month)
        #lsit of 5 strings
        self.top_5_names_in_arts = [i[0] for i in self.top_5_in_arts]

        self.top_5_artcats = artist_catalog.get_current_records().filter(artist_catalog.art_name.in_(self.top_5_names_in_arts)).order_by(artist_catalog.art_name).all()

        #filter down to the daily_arts charts that is just the top5
        self.arts_of_top5 = daily_artists.filter_by_year_month(year,month).filter(daily_artists.art_name.in_(self.top_5_names_in_arts)).order_by(daily_artists.art_name).all()

    def line_chart_components(self):
        dates = [i.date for i in self.arts_of_top5]
        positions = [i.position for i in self.arts_of_top5]
        art_names = [i.art_name for i in self.arts_of_top5]
        return dates, positions, art_names


class Artist_Catalog_Enriched:
    '''
    Holds together the data that will fill out the 'artist_history' plotly-dash.
    '''
    def __init__(self, art_id):
        self.art_id = art_id

        #daily Charts data:tracks
        self.track_hits = daily_tracks.artist_days_on_chart(art_id)
        self.track_streaks = utils.find_streaks_in_dates([i.date for i in self.track_hits])
        self.track_days = len(self.track_hits)
        #returns a list of song_names if this art_id has appearances in the daily_tracks charts
        self.notable_tracks = list(set(
            [i.song_name for i in self.track_hits]
        ))
        
        #daily_artists
        self.arts_hits = daily_artists.artist_days_on_chart(art_id)
        self.arts_streaks = utils.find_streaks_in_dates([i.date for i in self.arts_hits])
        self.arts_days = len(self.arts_hits)

        #returns a tuple that is ('date','int')
        self.longest_streak = utils.evaluate_longest_streak(
            self.track_streaks,
            self.arts_streaks
        )
        #art_cat data
        self.art_cat = artist_catalog.art_id_to_art_cat(art_id)

    def first_and_last_appearance(self):
        both_charts = self.track_hits + self.arts_hits
        all_dates = sorted([i.date for i in both_charts])
        first_date = all_dates[0]
        last_date = all_dates[-1]
        return first_date, last_date

    def scatter_plot_components(self):
        arts_triples = [
            (i.date, i.position, self.art_cat.art_name)
            for i in self.arts_hits]
        track_triples = [
            (i.date, i.position, i.song_name)
            for i in self.track_hits]
        both = arts_triples + track_triples
        x = [i[0] for i in both]
        y = [i[1] for i in both]
        z = [i[2] for i in both]
        return x,y,z
    
class Fred_Big_Dash_Stuff:
    '''
    Collects the data for populating the figures in the big_dash
    '''

    def __init__(
            self, 
            days_back_from_today,
            n_artists=3,
            ):
        self.rps = recently_played.get_rps_from_n_days_ago(days_back_from_today)
        self.dts = [i.last_played for i in self.rps]
        self.first_day = self.dts[0].date().isoformat()
        self.last_day = self.dts[-1].date().isoformat()
        self.known, self.unknown = recently_played.scan_for_art_cat_awareness(self.rps)
        self.top_artists = self.top_artists_in_rps(n_artists)
        self.top_tuples = self.top_n_counts_and_imgs(n_artists)
        self.mean_song_per_day = len(self.rps)/days_back_from_today
        self.top_rp = [i for i in self.rps if i.song_link[-22:] == self.song_counts()[0][0]][0]
        self.rando_master_genre_ac = artist_catalog.random_artist_in_genre(
            self.known_genre_counts()[0][0][0]
        )
        self.rando_subgenre_ac = artist_catalog.random_artist_in_subgenre(
            self.known_genre_counts()[1][0][0]
        )

    def top_artists_in_rps(self, n_artists=3):
        the_counter = Counter([
            i.art_name for i in self.rps
        ])
        art_names_tuples = the_counter.most_common(n_artists)
        art_names_in_order = [i[0] for i in art_names_tuples]
        return art_names_in_order
    
    def top_n_counts_and_imgs(self, n_artists=3):
        counts_imgs_tuples = []
        top_n_names = self.top_artists_in_rps(n_artists)
        for name in top_n_names:
            rps_of_name = [i for i in self.rps if i.art_name == name]
            top_song = Counter([i.song_name for i in rps_of_name]).most_common(1)[0][0]
            counts_imgs_tuples.append(
                (
                    name,
                    len(rps_of_name),
                    top_song,
                    rps_of_name[0].image,
                    rps_of_name[0].song_link
                ))
        return counts_imgs_tuples
    
    def known_genre_counts(self):
        '''
        Because of 'Los Ángeles Azules', this failed. That accent breaks the sql-alchemy query that uses art_name
        '''
        known_acs = list(map(
            artist_catalog.name_to_art_cat,
            self.known
        ))
        # Cut out the Nones. Like Los Angeles Azules. The RP schema should have art_id 2024-12-04
        known_acs = list(filter(
            None,
            known_acs
        ))
        known_master_genres = [i.master_genre for i in known_acs]

        known_genre_tuples = [(i.genre,i.genre2,i.genre3) for i in known_acs]
        eric_holder = []
        for tuplo in known_genre_tuples:
            for genre in tuplo:
                if genre != None:
                    eric_holder.append(genre)
        sub_count = Counter(eric_holder).most_common(10)
        master_count = Counter(known_master_genres).most_common(10)
        return master_count, sub_count
    
    def song_counts(self):
        top_songs = Counter(
            [i.song_link[-22:] for i in self.rps]
        ).most_common(10)
        return top_songs

    def avg_song_per_hour_Series(self):
        '''
        Returns a pandas series of float values of songs per hour, 24 items with 0 imputed
        for the missing values
        '''
        series_dts = pd.Series(self.dts)
        n_weeks = int(series_dts.dt.date.nunique() / 7)
        if n_weeks == 0:
            n_weeks = 1
        grouped_by_day_count = series_dts.groupby(series_dts.dt.hour).count()
        grouped_by_day = grouped_by_day_count / n_weeks

        # Reindex to include all hours of the day and fill missing values with 0
        grouped_by_day = grouped_by_day.reindex(range(24), fill_value=0)
        return grouped_by_day
    


def polar_chart_ingredients(date_obj):
    '''
    Returns two lists of 12 integers:
        am values,
        pm values,
    Polar Chart figure by default will use 0-11 as the hour label
    '''
    start, end = utils.first_and_last_dt_in_day(date_obj)
    rps = recently_played.get_timeframe_of_rp_records(start, end)
    date_times = [i.last_played for i in rps]
    hour_counts = recently_played.find_rps_per_hour(date_times)
    am_counts = {k:v for k,v in sorted(hour_counts.items()) if k < 12}
    am_values = list(am_counts.values())
    pm_counts = {k:v for k,v in sorted(hour_counts.items()) if k >= 12}
    pm_values = list(pm_counts.values())
    return date_obj, am_values, pm_values