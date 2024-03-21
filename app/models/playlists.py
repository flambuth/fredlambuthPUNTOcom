from app.extensions import db
from app.models.catalogs import artist_catalog

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy.orm import aliased


Base = declarative_base()

class Playlists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String())
    playlist_id = db.Column(db.String())
    track_id = db.Column(db.String())
    track_name = db.Column(db.String(150))
    art_id = db.Column(
        db.String(23),
        db.ForeignKey('artist_catalog.id', name='fk_daily_artists_art_id'),  # Provide a unique name here
        nullable=False
    )
    art_name = db.Column(db.String(150))
    duration = db.Column(db.Integer)
    added_at = db.Column(db.DateTime)


    @classmethod
    def filtered_enriched_playlist(self, playlist_id):
        filter_condition = and_(Playlists.playlist_id == playlist_id)
        filter_query = Playlists.query.filter(filter_condition)

        artist_alias = aliased(artist_catalog)
        result = filter_query\
            .outerjoin(artist_alias, Playlists.art_id == artist_alias.art_id)\
            .add_columns(
                artist_alias.img_url,  # Replace with the actual columns from artist_catalog
                artist_alias.master_genre,
            )\
            .all()
        return result