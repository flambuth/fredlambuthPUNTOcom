from app.blog import bp
from app.forms import SearchForm, CommentForm, SubmitBlogForm, SubmitPictureForm
from app.models.blog import blog_posts
from app.models.accounts import blog_comments
from app.models.charts import daily_tracks
from app.extensions import db
from app.utils import resize_image, resize_imageOLD

import os
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
from sqlalchemy import desc, func
from flask_login import login_required, current_user
from flask import render_template, request, redirect, url_for, flash, current_app

from datetime import date
#################################################
@bp.route('/blog', methods=['GET', 'POST'])
@bp.route('/blog/', methods=['GET', 'POST'])
def blog_landing_page():
    current_year = str(date.today().year)
    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    latest_3_posts = blog_posts.query.order_by(desc(blog_posts.id)).limit(3).all()

    all_yearmonths_index = blog_posts.year_month_blogpost_index()
    this_yearmonths_index = [i for i in all_yearmonths_index if i[0][:4]==current_year]

    all_years_index = blog_posts.year_of_blog_posts()
    prev_years_index = [i for i in all_years_index if i[0]!=current_year]

    medios_index = blog_posts.mediums_index()

    context = {
        'year_month_index' : this_yearmonths_index,
        'prev_years_index' : prev_years_index,
        'mediums_index' : medios_index,
        'latest_3_posts' : latest_3_posts,
        'form':searchform,
    }
    return render_template('blog/blog_landing_page.html', **context)

@bp.route('/blog/<string:year_month>', methods=['GET', 'POST'])
def blog_yearmonth_group(year_month):
    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    posts = blog_posts.query.filter(blog_posts.post_date.like(f'{year_month}%')).all()

    context = {
        'posts' : posts,
        'form':searchform,
    }
    return render_template('blog/blog_index.html', **context)

@bp.route('/blog/year/<string:year>', methods=['GET', 'POST'])
def blog_year_group(year):
    per_page = 6
    # Get the current page from request arguments, defaulting to 1
    page = request.args.get('page', 1, type=int)

    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    posts = blog_posts.query.filter(
        func.substr(blog_posts.post_date, 1, 4) == year
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    context = {
        'posts' : posts.items,
        'form':searchform,
        'page': page,
        'year': year,
        'total_pages': posts.pages,
        'prev_page': posts.prev_num,
        'next_page': posts.next_num,
    }
    return render_template('blog/blog_index.html', **context)

@bp.route('/blog/review/<string:medium>', methods=['GET', 'POST'])
def blog_about_this_medium(medium):
    per_page = 6
    # Get the current page from request arguments, defaulting to 1
    page = request.args.get('page', 1, type=int)

    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    
    #posts = blog_posts.query.filter(blog_posts.medium == medium).all()
    paginated_posts = blog_posts.query.filter(blog_posts.medium == medium).order_by(
        desc(blog_posts.post_date)
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    context = {
        'posts': paginated_posts.items,
        'form': searchform,
        'page': page,
        'medium': medium,
        'total_pages': paginated_posts.pages,
        'prev_page': paginated_posts.prev_num,
        'next_page': paginated_posts.next_num,
    }
    return render_template('blog/blog_index.html', **context)



@bp.route('/blog/search/<string:search_term>', methods=('GET','POST'))
@login_required
def blog_index_search(search_term):
    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))

    blogs_like = blog_posts.content.like(f"%{search_term}%")
    blog_matches = blog_posts.query.filter(blogs_like).order_by(desc('id')).all()

    context = {
        'posts':blog_matches,
        'form':searchform,
    }

    return render_template('blog/blog_index.html', **context)

########
@bp.route('/blog/post/<int:post_id>', methods=['GET', 'POST'])
def blog_single(post_id):
    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    max_id = db.session.query(func.max(blog_posts.id)).all()[0][0]
    if post_id==max_id:
        next_post=None
    else:
        next_post = blog_posts.query.filter(blog_posts.id==post_id+1).all()[0]
    post = blog_posts.query.filter(blog_posts.id==post_id).all()[0]

    if post_id==1:
        prev_post=None
    else:
        prev_post = blog_posts.query.filter(blog_posts.id==post_id-1).all()[0]

    top_3_songs = daily_tracks.random_n_tracks_that_day(post.iso_date)
    post_comments = blog_comments.query.filter_by(post_id=post_id).all()

    context = {
        'post' : post,
        'prev_post' : prev_post,
        'next_post' : next_post,
        'top_3_songs' : top_3_songs,
        'form':searchform,
        'comments': post_comments,
    }
    return render_template('blog/blog_single.html', **context)

#####################
###comments
@bp.route('/blog/add_comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def blog_add_comment(post_id):
    form = CommentForm()
    post = blog_posts.query.filter(blog_posts.id==post_id).all()[0]

    if form.validate_on_submit():
        new_comment = blog_comments(
            content=form.content.data,
            post_id=post_id,
            user_id=current_user.id,
            comment_date=datetime.utcnow()
        )

        db.session.add(new_comment)
        db.session.commit()

        flash('Your comment has been added!', 'success')
        return redirect(url_for('blog.blog_single', post_id=post_id))

    return render_template('blog/blog_add_comment.html', post=post, form=form)

@bp.route('/upload_blog_post', methods=['GET', 'POST'])
@login_required
def submit_blog_post():
    #UPLOAD_FOLDER = '/static/img/blog_pics/'
    #ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    form = SubmitBlogForm()
    latest_blog_id = str(blog_posts.last_post_id() + 1)
    test_file_name = f'pic_{latest_blog_id}.jpg'
    filename = secure_filename(test_file_name)
    print(filename)

    blog_pic_dir = '/home/flambuth/fredlambuthPUNTOcom/app/static/img/blog_pics/'
    
    if current_user.username != 'eddie_from_chicago':
        flash("You are not authorized to submit a blog post.")
        return redirect(url_for('user_accounts.login'))

    if form.validate_on_submit():

        print("Form data:", form.data)

        
        if form.picture.data:

            input_path = blog_pic_dir + filename
            print("File to be Saved:", input_path)
            form.picture.data.save(input_path)
            print("File saved to input path")

        new_post = blog_posts(
            title=form.title.data,
            content=form.content.data,
            medium=form.medium.data.lower(),
            post_date=datetime.today().strftime('%Y-%b-%d'))

        db.session.add(new_post)
        db.session.commit()

        
        return redirect(url_for('blog.blog_landing_page'))

    else:
        # Form submission failed validation
        # Print validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in field '{field}': {error}")
                print(f"Error in field '{field}': {error}")
        return render_template('blog/blog_add_post.html', title='Register', form=form)