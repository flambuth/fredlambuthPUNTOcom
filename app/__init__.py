from flask import Flask, render_template, send_file, g
from flask_login import LoginManager
#from flask_caching import Cache
from flask_migrate import Migrate

from datetime import datetime

from config import Config
from config import SECRET_KEY

from app.extensions import db

login_manager = LoginManager()

#for spotify img links!
#https://i.scdn.co/image/

def create_app(config_class=Config):
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object(config_class)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png', 'jpeg'}

    login_manager.init_app(app)
    login_manager.login_view = 'user_accounts.login'

    db.init_app(app)
    migrate = Migrate(app, db)

    from app.spotify import cache
    cache.init_app(app)

    from app.user_accounts import bp as accounts_bp
    app.register_blueprint(accounts_bp)

    from app.spotify import bp as main_bp
    app.register_blueprint(main_bp)

    from app.blog import bp as blog_bp
    app.register_blueprint(blog_bp)

    from app.podcast import bp as podcast_bp
    app.register_blueprint(podcast_bp)

    @app.route('/')
    def homepage():
        return render_template('homepage.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')


    #break into new app
    @app.route('/about_me')
    def about_me():
        return render_template('about_me.html')
    
    @app.route('/resume')
    def serve_resume_pdf():
        filename = 'static/Fredrick_Lambuth_Resume.pdf'
        return send_file(filename, as_attachment=False)

    @app.route('/online_resume')
    def online_resume():
        return render_template('online_resume.html')

    @app.before_request
    def before_request():
        g.current_year = datetime.now().year
        g.current_month = datetime.now().month

    from app.dash_plotlys.dash_apps.year_month_line_chart import Add_Dash_year_month
    Add_Dash_year_month(app)

    from app.dash_plotlys.dash_apps.artist_history import Add_Dash_art_cat
    Add_Dash_art_cat(app)

    from app.dash_plotlys.dash_apps.big_dash import Add_Big_Dash
    Add_Big_Dash(app)

    #from app.dash_plotlys.dash_apps.global_dash_lite import Add_Dash_global_view_lite
    #Add_Dash_global_view_lite(app)

    from app.dash_plotlys.dash_apps.country_today_tracks import Add_Dash_today_tracks_in_country
    Add_Dash_today_tracks_in_country(app)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
