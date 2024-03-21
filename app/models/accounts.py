from app.extensions import db
from app import login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
#from app.models.commentsOLD import BlogComments

class user_accounts(UserMixin, db.Model):
    '''
    User account that will have the ability to comment on:
        blog_posts,
        other user_account homepages, (soon)
        spotify pages, (soon)

    Also do usuall user_account stuff like change password, or change profile_pic
    '''
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    #User stats
    @classmethod
    def blog_user_stats(cls, blog_user_id):
        blog_user_comments = blog_comments.query.filter(blog_comments.user_id == blog_user_id).all()
        if blog_user_comments:
            comment_count = len(blog_user_comments)
            start_date = blog_user_comments[0].comment_date.isoformat()[:10]
        else:
            comment_count = 0
            start_date = datetime.now().isoformat()[:10]
        return comment_count, start_date

    @classmethod
    def all_users_stats(cls):
        users = cls.query.with_entities(cls.id, cls.username).all()
        users_ids = [i[0] for i in users]
        users_names = [i[1] for i in users]
        user_stats = list(map(
            cls.blog_user_stats,
            users_ids
        ))
        user_stats = list(zip(users_names, user_stats))
        return user_stats

    #PASSWORD STUFF
    @classmethod
    def set_password(cls, password):
        return generate_password_hash(password)

    @classmethod
    def change_password(cls, username, new_password):
        user = cls.query.filter_by(username=username).first()

        if user:
            # Set the new hashed password
            user.password_hash = cls.set_password(new_password)

            # Commit the changes to the database
            db.session.commit()

            return True  # Password changed successfully
        else:
            return False  # User not found

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Configure user loader for LoginManager outside of the model
    @login_manager.user_loader
    def load_user(user_id):
        return user_accounts.query.get(user_id)

    def __repr__(self):
        return f'<User_Account: "{self.username}">'
    
class blog_comments(db.Model):
    '''
    Comment made by user on blog_posts in the blog model
    Each user can make as many comments as they want on each blog_post
    '''
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)

    post = db.relationship('blog_posts', backref=db.backref('comments', lazy=True))
    user = db.relationship('user_accounts', backref=db.backref('comments', lazy=True))
    
    comment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment by {self.user.username} on post "{self.post.title}">'
    
class artist_comments(db.Model):
    '''
    Comment made by user on artist catalogs in the catalogs module
    Each user can make as many comments as they want on each artist catalog
    '''
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    artist_catalog_id = db.Column(db.Integer, db.ForeignKey('artist_catalog.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_accounts.id'), nullable=False)

    artist_catalog = db.relationship('artist_catalog', backref=db.backref('artist_comments', lazy=True))
    user = db.relationship('user_accounts', backref=db.backref('artist_comments', lazy=True))
    
    comment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ArtistComment by {self.user.username} on artist catalog "{self.artist_catalog.name}">'