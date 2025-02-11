from app.extensions import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, or_, desc, and_

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
    def all_art_ids_in_cat(cls):
        '''
        List so you can check if the charts models have art_ids not in the catalog
        '''
        unique_art_ids = [i[0] for i in cls.query.with_entities(cls.art_id).distinct().all()]
        return unique_art_ids

    @classmethod
    def get_current_records(cls):
        return cls.query.filter_by(is_current=True)
    
    #this one is the archival view of non_current records
    @classmethod
    def get_inactive_records(cls):
        return cls.query.filter_by(is_current=False)

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

    @classmethod
    def all_distinct_genres(cls):
        uno = list(set([i[0] for i in cls.get_current_records().with_entities(cls.genre).distinct().all()]))
        dos = list(set([i[0] for i in cls.get_current_records().with_entities(cls.genre2).distinct().all()]))
        tres = list(set([i[0] for i in cls.get_current_records().with_entities(cls.genre3).distinct().all()]))
        all_distinct_genres = list(set(uno + dos + tres))
        esto = sorted([i for i in all_distinct_genres if i is not None])
        return esto
    
    @staticmethod
    def artists_in_genre(genre):
        genre = genre.lower()
        matching_arts_query = (
        artist_catalog.get_current_records()
        .filter(
            or_(
                func.lower(artist_catalog.genre)==genre,
                func.lower(artist_catalog.genre2)==genre,
                func.lower(artist_catalog.genre3)==genre,
            )
        )).order_by('art_name')
        results = matching_arts_query.all()
        return results
    
    @staticmethod
    def genre_dictionary():
        '''
        Returns a dictionary with all genres in found in the art_cat as keys
        lists of art_cat objs as values
        '''
        blob_list = artist_catalog.all_distinct_genres()
        genre_bookings = { genre: artist_catalog.artists_in_genre(genre) for genre in blob_list}
        return genre_bookings

    @classmethod
    def add_new_art_cat_to_db(cls, new_art_cat):
        '''
        Takes a art_cat object as a parameter and add's it
        to the database
        
        unless the art_id can be found in the art_cat
        '''
        if new_art_cat.art_id in cls.all_art_ids_in_cat():
            print('art_id already exists')
        else:
            db.session.add(new_art_cat)
            db.session.commit()

    @classmethod
    def add_refreshed_art_cat_to_db(cls, refreshed_art_cat):
        '''
        Takes a recently_played object as a parameter and add's it
        to the database
        Updates all records with art_id to be set as not active
        '''
        try:
            # Add the new record to the database
            db.session.add(refreshed_art_cat)

            # Define the condition for the update
            condition = and_(
                artist_catalog.art_id == refreshed_art_cat.art_id,
                artist_catalog.app_record_date != refreshed_art_cat.app_record_date
            )

            # Update the is_active field to False for matching records
            artist_catalog.query.filter(condition).update(
                {artist_catalog.is_current: False},
                synchronize_session=False
            )

            # Commit the changes to the database
            db.session.commit()
            
            # Print statement to indicate progress
            print(f"Refreshed and added to DB: {refreshed_art_cat.art_name}")
        
        except Exception as e:
            # Rollback the session in case of an error
            db.session.rollback()
            raise e

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
    
    @staticmethod
    def genre_counts():
        group_counts = db.session.query(
        artist_catalog.genre,
        (
            func.sum(artist_catalog.genre.isnot(None).cast(db.Integer)) +
            func.sum(artist_catalog.genre2.isnot(None).cast(db.Integer)) +
            func.sum(artist_catalog.genre3.isnot(None).cast(db.Integer))
        ).label('total_count')
        ).filter(
            artist_catalog.is_current == True
            ).group_by(
                artist_catalog.genre
                ).order_by(desc('total_count')).all()

        return group_counts

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
    def add_new_track_cat_to_db(cls, new_track_cat):
        '''
        Accepts a track_catalog type object and saves it to the track_catalog table in sqlite
        '''
        if new_track_cat.song_id in cls.all_song_ids_in_cat():
            print('song_id already exists')
        else:
            db.session.add(new_track_cat)
            db.session.commit()

    @classmethod
    def all_song_ids_in_cat(cls):
        '''
        List so you can check if the charts models have art_ids not in the catalog
        '''
        unique_song_ids = [i[0] for i in cls.query.with_entities(cls.song_id).all()]
        return unique_song_ids

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

    ##########RP Inspection
    @classmethod
    def know_this_track(cls, rp_obj):
        for_sure = cls.song_id_to_track_cat(rp_obj.song_link[-22:])
        if for_sure:
            return True
        
        maybe = cls.find_song_in_track_cat(rp_obj.song_name)
        maybe_art_name = cls.song_id_to_track_cat(maybe)
        if maybe_art_name == rp_obj.art_name:
            return True
        
        else:
            return False



    def __repr__(self):
        return f'<track_cat_entry "{self.song_name}">'