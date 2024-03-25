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

#################################################
@bp.route('/blog', methods=['GET', 'POST'])
@bp.route('/blog/', methods=['GET', 'POST'])
def blog_landing_page():
    searchform = SearchForm()
    if request.method == 'POST':
        return redirect(url_for('blog.blog_index_search', search_term=searchform.search_term.data))
    latest_6_posts = blog_posts.query.order_by(desc(blog_posts.id)).limit(6).all()

    context = {
        'year_month_index' : blog_posts.year_month_blogpost_index(),
        'latest_6_posts' : latest_6_posts,
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

    blog_pic_dir = '/home/flambuth/new_fred/app/static/img/blog_pics/'
    
    if form.validate_on_submit():

        print("Form data:", form.data)

        # Check if the provided account creation password is correct
        if form.picture.data:

            # Constructing the final paths
            input_path = blog_pic_dir + filename

            print("File to be Saved:", input_path)

            # Save and resize the uploaded file
            form.picture.data.save(input_path)
            print("File saved to input path")

        new_post = blog_posts(
            title=form.title.data,
            content=form.content.data,
            post_date=datetime.today().strftime('%Y-%b-%d'))

        db.session.add(new_post)
        db.session.commit()

        # login_user(new_user)  # Automatically log in the new user after registration
        return redirect(url_for('blog.blog_landing_page'))

    else:
        # Form submission failed validation
        # Print validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in field '{field}': {error}")
                print(f"Error in field '{field}': {error}")
        return render_template('blog/blog_add_post.html', title='Register', form=form)