from app.extensions import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, or_, case
#from .main import daily_tracks

Base = declarative_base()

class artist_catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_id = db.Column(db.String(22))
    art_name = db.Column(db.String(150))
    followers = db.Column(db.Integer)
    genre = db.Column(db.String(70))
    genre2 = db.Column(db.String(70))
    genre3 = db.Column(db.String(70))
    img_url = db.Column(db.String(150))
    img_url_mid = db.Column(db.String(150))
    img_url_sml = db.Column(db.String(150))
    master_genre = db.Column(db.String(150))
    app_record_date = db.Column(db.String(150))
    is_current = db.Column(db.Boolean)

    #use this one in the views so that there are not duplicates of each artist
    #this will trim it down to the latest record
    @classmethod
    def get_current_records(cls):
        return cls.query.filter_by(is_current=True)
    
    #this one is the archival view of non_current records
    @classmethod
    def get_inactive_records(cls):
        return cls.query.filter(cls.is_current.is_(None)).all()

    @classmethod
    def count_active_records_by_genre(cls):
        '''
        Returns the count of active records for each genre
        '''
        active_genre_counts = db.session.query(
            cls.master_genre,
            func.count().label('Active Records')
        ).filter(
            cls.is_current.is_(True)
        ).group_by(
            cls.master_genre
        ).order_by(
            func.count().desc()
        ).all()
        return active_genre_counts

    def __repr__(self):
        return f'<art_cat_entry "{self.art_name}">'
    
    def __str__(self):
        return f'Artist Catalog Entry For: "{self.art_name}">'

    @staticmethod
    def find_name_in_art_cat(test_name):
        '''
        Accepts a test string to search in the art_name field of the artist catalog.
        Returns None if nothing is found
        '''
        #input and art_cat.art_name are both lowered before evaluating for match
        test_name_lowered = test_name.lower()
        results = artist_catalog.query.filter(
            func.lower(artist_catalog.art_name) == test_name_lowered
    ).all()
        if not results:
            # Handle the case where no match is found
            return None
        
        #returns the art_id if there is a match
        return results[0].art_id
    
    @staticmethod
    def art_id_to_art_cat(art_id):
        '''
        Takes an art_id, returns the art_cat record if there is one.
        '''
        result = artist_catalog.query.filter(artist_catalog.art_id==art_id).first()
        if not result:
            # Handle the case where no match is found
            return None

        return result
    
    @staticmethod
    def name_to_art_cat(art_name):
        '''
        Takes an art_id, returns the art_cat record if there is one.
        '''
        result = artist_catalog.art_id_to_art_cat(
            artist_catalog.find_name_in_art_cat(art_name)
        )
        return result

    @staticmethod
    def random_artist_in_genre(genre):
        '''
        Adds some randomness to pick from one genre.
        '''
        rando = (
        artist_catalog.query.filter(artist_catalog.master_genre == genre
        ).order_by(func.random()
        ).limit(1).first()
        )
        return rando
    
    @staticmethod
    def random_artist_in_subgenre(genre):
        '''
        Adds some randomness to pick from one genre.
        '''
        rando = (
            artist_catalog.query.filter(
                or_(
                    artist_catalog.genre == genre,
                    artist_catalog.genre2 == genre,
                    artist_catalog.genre3 == genre
                )
            ).order_by(func.random()
            ).limit(1).first()
        )
        return rando
    
    @staticmethod
    def artists_within_genre(genre):
        '''
        Returns a list of artist names that have the same master_genre as the input parameter.
        '''
        genre_ac_names = [
            i[0] for i in
            artist_catalog.query.filter(artist_catalog.master_genre==genre).with_entities(artist_catalog.art_name).distinct().all()
        ]
        return genre_ac_names

class track_catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    art_name = db.Column(db.String(150))
    album_id = db.Column(db.String())
    album_name = db.Column(db.String(150))
    song_id = db.Column(db.String(70))
    song_name = db.Column(db.String(270))
    img_url = db.Column(db.String(150))
    duration = db.Column(db.Integer)
    app_record_date = db.Column(db.String(150))

    @classmethod
    def count_tracks_by_first_letter(cls):
        query = db.session.query(func.substr(track_catalog.song_name, 1, 1).label('first_char'), func.count().label('count'))
        result = query.group_by('first_char').all()

        #the index slicing at the end is to get rid of an umlaut and a weird C
        counts = [i for i in result if (i[0].isalnum() & i[0].isupper())][:-2]
        return counts
    
    @classmethod
    def all_tracks_starting_with(
        cls,
        letter):
        '''
        Returns a list of track_cat results where the song_name begins with the 
        parameter value
        '''
        
        start_with_letter = cls.query.filter(
            cls.song_name.startswith(letter.upper())
                ).order_by('song_name').all()
        
        track_letter_results = start_with_letter
        return track_letter_results

    @classmethod
    def random_track_by_letter(
        cls,
        letter):
        '''
        Returns one randomly chosen track objects that starts with the parameter letter
        '''
        rando = (
        cls.query.filter(func.substring(cls.song_name,1,1) == letter.upper()
        ).order_by(func.random()
        ).limit(1).first()
        )
        return rando
    
    @staticmethod
    def find_song_in_track_cat(test_name):
        '''
        Accepts a test string to search in the song_name field of the track catalog.
        Returns None if nothing is found
        '''
        #both lowered before evaluating for match
        test_name_lowered = test_name.lower()
        results = track_catalog.query.filter(
            func.lower(track_catalog.song_name) == test_name_lowered
    ).all()
        if not results:
            # Handle the case where no match is found
            return None
        
        #returns the art_id if there is a match
        return results[0].song_id
    
    @staticmethod
    def song_id_to_track_cat(song_id):
        '''
        '''
        result = track_catalog.query.filter(track_catalog.song_id==song_id).first()
        if not result:
            # Handle the case where no match is found
            return None

        return result

    @classmethod
    def track_cat_landing_thruples(cls):
        '''
        Returns 26 three-part tuples containing letter, count, img_url code for a rando starting with the letter
        '''
        alpha_counts = track_catalog.count_tracks_by_first_letter()
        alpha_tracks = list(map(
            track_catalog.random_track_by_letter,
            [i[0] for i in alpha_counts]
        ))
        alpha_imgs = [i.img_url for i in alpha_tracks]
        thruples = list(zip(
            [i[0] for i in alpha_counts], [i[1] for i in alpha_counts], alpha_imgs
            ))
        return thruples

    def __repr__(self):
        return f'<track_cat_entry "{self.song_name}">'