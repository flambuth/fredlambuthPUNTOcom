from app.extensions import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, extract

import random
from datetime import timedelta
from collections import Counter

from app.models.catalogs import artist_catalog, track_catalog

Base = declarative_base()

class daily_tracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    #art_id = db.Column(db.String(23))
    art_id = db.Column(
        db.String(23),
        db.ForeignKey('artist_catalog.id'),
        nullable=False)
    art_name = db.Column(db.String(150))
    album_name = db.Column(db.String(150))
    song_id = db.Column(db.String(23))
    song_name = db.Column(db.String(150))
    date = db.Column(db.Date, nullable=False)
    
    def __repr__(self):
        return f'<daily_tracks for "{self.date}">'
    
    @classmethod
    def all_art_ids_in_chart_history(cls):
        '''
        List so you can check if the charts models have art_ids not in the catalog
        '''
        unique_art_ids = list(set(
            [i[0] for i in cls.query.with_entities(cls.art_id).all()]
        ))
        return unique_art_ids
    
    
    @classmethod
    def ids_not_in_art_cat(cls):
        '''
        Finds all art_ids in the daily tables that are not found in the artist catalog.
        '''
        art_cat_ids = artist_catalog.all_art_ids_in_cat()
        tracks_ids = cls.all_art_ids_in_chart_history()
        new_ids = [i for i in tracks_ids if i not in art_cat_ids ]
        return new_ids
    
    @classmethod
    def song_ids_not_in_track_cat(cls):
        '''
        Scans the daily_tracks table for new song_ids
        '''
        missing_tracks_query = db.session.query(cls.song_id).outerjoin(
            track_catalog, cls.song_id == track_catalog.song_id
        ).filter(track_catalog.song_id == None).distinct()

        missing_tracks = missing_tracks_query.all()

        # song_id values from the query result
        missing_song_ids = [track.song_id for track in missing_tracks]
        return missing_song_ids

    @classmethod
    def add_daily_chart_to_db(cls, new_daily_chart):
        '''
        Takes a recently_played object as a parameter and add's it
        to the database
        '''
        db.session.add(new_daily_chart)
        db.session.commit()

    @staticmethod
    def get_latest_date():
        latest_date = db.session.query(func.max(daily_tracks.date)).scalar()
        return latest_date
    
    @classmethod
    def top_n_tracks_that_day(
        cls,
        iso_date,
        n=3):
        '''
        Returns n amount of 1-n songs on a given iso-date.
        '''
        print(f"Calling top_n_tracks_that_day with iso_date: {iso_date}")
        top_n_songs = cls.query.filter(
            cls.date == iso_date
        ).all()[:n]
        return top_n_songs

    @classmethod
    def random_n_tracks_that_day(cls, iso_date, n=3):
        '''
        Returns a random selection of n songs on a given iso-date.
        '''
        print(f"Calling random_n_tracks_that_day with iso_date: {iso_date}")
        
        # Fetch all songs for the given iso_date
        all_songs_that_day = cls.query.filter(cls.date == iso_date).all()

        # Ensure that n is not greater than the total number of songs available
        n = min(n, len(all_songs_that_day))

        # Randomly select n songs
        random_songs = random.sample(all_songs_that_day, n)

        return random_songs

    @classmethod
    def filter_by_year_month(cls, year, month):
        '''
        Filters the records for a particular year and month.
        :param year: The year (integer)
        :param month: The month (integer)
        :return: Query result for the specified year and month
        '''
        return cls.query.filter(
            extract('year', cls.date) == year,
            extract('month', cls.date) == month
        )

    @classmethod
    def hits_in_year_month(
        cls,
        year,
        month,
        n=5
    ):
        result = (
        cls.filter_by_year_month(year, month)
        .group_by(cls.art_name)
        .with_entities(
            cls.art_name,
            func.sum(21 - cls.position).label('chart_power_sum')
        )
        .order_by(func.sum(21 - cls.position).desc())
        .all()
    )
        return result[:n]


    @classmethod
    def artist_days_on_chart(
            cls,
            art_id):
        '''
        Given an art_id returns the chart results if they are in the model
        '''
        art_days = cls.query.filter(cls.art_id == art_id).all()
        return art_days

    
class daily_artists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    art_id = db.Column(
        db.String(23),
        db.ForeignKey('artist_catalog.id', name='fk_daily_artists_art_id'),  # Provide a unique name here
        nullable=False
    )
    art_name = db.Column(db.String(150))
    date = db.Column(db.Date(), nullable=False)

    def __repr__(self):
        return f'<daily_artists for "{self.date}">'

    @staticmethod
    def get_latest_date():
        latest_date = db.session.query(func.max(daily_artists.date)).scalar()
        return latest_date

    @classmethod
    def all_art_ids_in_chart_history(cls):
        '''
        List so you can check if the charts models have art_ids not in the catalog
        '''
        unique_art_ids = list(set(
            [i[0] for i in cls.query.with_entities(cls.art_id).all()]
        ))
        return unique_art_ids
    
    @classmethod
    def ids_not_in_art_cat(cls):
        art_cat_ids = artist_catalog.all_art_ids_in_cat()
        arts_ids = cls.all_art_ids_in_chart_history()
        new_ids = [i for i in arts_ids if i not in art_cat_ids ]
        return new_ids

    @classmethod
    def add_daily_chart_to_db(cls, new_daily_chart):
        '''
        Takes a recently_played object as a parameter and add's it
        to the database
        '''
        db.session.add(new_daily_chart)
        db.session.commit()

    @classmethod
    def filter_by_year_month(cls, year, month):
        '''
        Filters the records for a particular year and month.
        :param year: The year (integer)
        :param month: The month (integer)
        :return: Query result for the specified year and month
        '''
        return cls.query.filter(
            extract('year', cls.date) == year,
            extract('month', cls.date) == month
        )

    @classmethod
    def hits_in_year_month(
        cls,
        year,
        month,
        n=5
    ):
        result = (
        cls.filter_by_year_month(year, month)
        .group_by(cls.art_name)
        .with_entities(
            cls.art_name,
            func.sum(21 - cls.position).label('chart_power_sum')
        )
        .order_by(func.sum(21 - cls.position).desc())
        .all()
    )
        return result[:n]

    @classmethod
    def artist_days_on_chart(
            cls,
            art_id):
        '''
        Given an art_id returns the chart results if they are in the model
        '''
        art_days = cls.query.filter(cls.art_id == art_id).all()
        return art_days



###########
#THIS MIGHT BE BETTER OF as a third module in the models library
class recently_played(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_name = db.Column(db.String(150))
    song_name = db.Column(db.String(150))
    song_link = db.Column(db.String(150))
    image = db.Column(db.String(150))
    last_played = db.Column(db.DateTime)

    @classmethod
    def add_rp_to_db(cls, new_rp):
        '''
        Takes a recently_played object as a parameter and add's it
        to the database
        '''
        db.session.add(new_rp)
        db.session.commit()

    @classmethod
    def get_latest_song(cls):
        latest_record = cls.query.order_by(cls.id.desc()).first()
        if latest_record:
            return latest_record
        else:
            return None


    @classmethod
    def get_timeframe_of_rp_records(
        cls,
            start_datetime,
            end_datetime
    ):
        '''
        Now takes datetimes! Because I changed the 'last_played' field to be a SQLAlchemy Datetime type instead of string!
        2024_02_20
        '''
        timeframe_of_rps = cls.query.filter(
        cls.last_played >= start_datetime,#.strftime('%Y-%m-%dT%H:%M:%S'),
        cls.last_played <= end_datetime#.strftime('%Y-%m-%dT%H:%M:%S')
        ).all()
        return timeframe_of_rps
    

    @staticmethod
    def find_rps_per_hour(date_times):
        '''
        Input should be a list of rp object within the same calendar day
        Returns a Collection dict with 0-23 hrs as keys, the rps per hour in that day as values
        '''
        rps_per_hour = Counter([i.hour for i in date_times])
        missing_hours = [i for i in range(24) if i not in rps_per_hour.keys()]
        #imputes 0 for hours with no RPs
        for i in missing_hours:
            rps_per_hour[i]=0
        return rps_per_hour


    @classmethod
    def past_24_hrs_rps(cls):
        '''
        Uses get_timeframe_of_rp_records on a 24 hour timeframe that is ends 24 hours from the time the function is called
        '''
        latest_datetime = cls.query.order_by(cls.id.desc()).first().last_played
        #latest_datetime = datetime.strptime(latest_datetime, '%Y-%m-%dT%H:%M:%S')
        start_datetime =  latest_datetime - timedelta(hours=48)
        end_datetime = latest_datetime - timedelta(hours=24)
        rps_from_past24 = cls.get_timeframe_of_rp_records(start_datetime, end_datetime)
        return rps_from_past24
    
    @classmethod
    def get_rps_from_n_days_ago(cls, n):
        delta = timedelta(days=n)
        start_date = cls.latest_played_datetime() - delta
        #end_date = cls.latest_played_datetime()
        rps = cls.query.filter(cls.last_played >= start_date).all()
        return rps

    @classmethod
    def scan_for_art_cat_awareness(
        cls,
        rps):
        '''
        Returns a 2-tuple. Each element is a list. First is art_names found in the past_24_hrs_rps, 
        second are the art_names that do not
        
        art_names = cls.past_24_hrs_rps()]
        '''

        yesterday_art_names=list(set([i.art_name for i in rps]))
        heard_of_em = artist_catalog.query.filter(artist_catalog.art_name.in_(yesterday_art_names)).all()
        heard_of_em_names = list(set([i.art_name for i in heard_of_em]))
        not_heard_of_em_names = list(set([i for i in yesterday_art_names if i not in heard_of_em_names]))
        return heard_of_em_names, not_heard_of_em_names

    @classmethod
    def rp_average_per_day(cls):
        '''
        This only goes back 100 days now, so this should be retitled to 100 day average
        '''
        result = db.session.query(
        func.date(cls.last_played).label('play_date'),
        func.count().label('record_count')
        ).group_by('play_date').all()
        daily_avg = sum(i[1] for i in result) / len(result) 
        return int(daily_avg)

    @classmethod
    def latest_played_datetime(cls):
        latest_record = cls.query.order_by(cls.last_played.desc()).first()
        if latest_record:
            return latest_record.last_played
        else:
            return None
    
    @staticmethod
    def cat_scan_rp_object(rp_obj):
        if track_catalog.know_this_track(rp_obj):
            rp_obj.known_track = True
        else:
            rp_obj.known_track = False

        if artist_catalog.find_name_in_art_cat(rp_obj.art_name):
            rp_obj.known_artist = True
        else:
            rp_obj.known_artist = False

        return rp_obj


    def __repr__(self):
        return f'<recently_played for "{self.art_name}" listend to at "{self.last_played}">'
    