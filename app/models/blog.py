from app.extensions import db
#from app import login_manager
from datetime import datetime
#from flask_login import UserMixin
from sqlalchemy import func
#from werkzeug.security import check_password_hash, generate_password_hash

def convert_to_iso_date(date_string):
    return datetime.strptime(date_string, '%Y-%b-%d').isoformat()[:10]

class blog_posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.String(20), nullable=False)
    medium = db.Column(db.String(50))
    theme1 = db.Column(db.String(50))
    theme2 = db.Column(db.String(50))

    @property
    def iso_date(self):
        return convert_to_iso_date(self.post_date)
    
    @classmethod
    def last_post_id(cls):
        last_id = cls.query.with_entities(cls.id).all()[-1][0]
        return last_id

    @classmethod
    def mediums_index(cls):
        medium_counts = db.session.query(
            cls.medium, func.count()
            ).group_by(cls.medium).order_by(func.count().desc()).all()
        return medium_counts

    @classmethod
    def year_month_blogpost_index(cls):
        result = (
            db.session.query(
                func.substr(cls.post_date, 1, 8).label('year_month'),
                func.count().label('post_count')
            )
            .group_by('year_month')
            .order_by('year_month')  # Optional: Order the results by year-month
            .all()
        )

        #does a quick sort by changing the 2023-JAN string to a measurable date 
        datetime_result = [(datetime.strptime(i[0], '%Y-%b'),i[1]) for i in result]
        sorted_data = sorted(datetime_result, key=lambda x: x[0])
        sorted_strings = [(datetime.strftime(date_str, "%Y-%b"), post_count) for date_str, post_count in sorted_data]
        return sorted_strings

    @classmethod
    def year_of_blog_posts(cls):
        result = (
            db.session.query(
                func.substr(cls.post_date, 1, 4).label('year'),
                func.count().label('post_count')
            )
            .group_by('year')
            .order_by('year')  # Optional: Order the results by year-month
            .all()
        )

        #does a quick sort by changing the 2023-JAN string to a measurable date 
        #datetime_result = [(datetime.strptime(i[0], '%Y-%b'),i[1]) for i in result]
        #sorted_data = sorted(datetime_result, key=lambda x: x[0])
        #sorted_strings = [(datetime.strftime(date_str, "%Y-%b"), post_count) for date_str, post_count in sorted_data]
        return result

    def __repr__(self):
        return f'<Post "{self.title}">'
