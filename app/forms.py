from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, DataRequired, Email, EqualTo, ValidationError
from flask import current_app

class SearchForm(FlaskForm):
    '''
    Used in the blog search bar.
    '''
    search_term = StringField('Search: ', validators=[InputRequired(),
                                             Length(min=1, max=100)])

class LoginForm(FlaskForm):
    '''
    For loggin in users to make comments on blog posts.
    '''
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    '''
    New Users make one of these. The data collected from this will match with the required fields of
    the blog_user model
    '''
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    account_creation_password = PasswordField('Account Creation Password', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Only jpg, jpeg, and png files under 5mb')])
    submit = SubmitField('Register')

    def validate_account_creation_password(self, field):
        '''
        method used for only requiring the user to submit a user_account_creation password.
        '''
        required_password = current_app.config.get('BLOG_PSWD')
        if field.data != required_password:
            raise ValidationError('Invalid account creation password.')
        
class CommentForm(FlaskForm):
    '''
    Form generated when the 'add a comment' button is used in the blog_single template
    '''
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')

class SubmitPictureForm(FlaskForm):
    '''
    Just for the change_profile_picture route available to logged in users
    '''
    allowed_extensions = ['jpg', 'jpeg','png']
    max_file_size = 5 * 1024 * 1024  # 5 MB

    pic_file = FileField(
        'Profile Picture',
        validators=[
            FileAllowed(allowed_extensions, 'Only .jpg, .jpeg, and .png files under 5mb allowed!'),
            lambda form, field: form.validate_file_size(field)
        ]
    )
    submit = SubmitField('Submit Photo')

    def validate_file_size(self, field):
        if field.data:
            file_size = len(field.data.read())
            field.data.seek(0)  # Reset file pointer to the beginning
            if file_size > self.max_file_size:
                raise ValidationError('File size exceeds the maximum allowed (5 MB). Please choose a smaller file.')
            

class SubmitBlogForm(FlaskForm):
    '''
    THIS ONE
    '''
    title = StringField('Title', validators=[DataRequired(), Length(min=4, max=150)])
    content = TextAreaField('Content', validators=[DataRequired()])
    medium = StringField('Medium', validators=[DataRequired(), Length(min=2, max=50)])

    picture = FileField('Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Only jpg, jpeg, and png files under 5mb')])
    submit = SubmitField('Register')

'''
class BlogPostFormWHAT(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=150)])
    content = TextAreaField('Content', validators=[InputRequired()])

    blog_picture = FileField('Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Only jpg, jpeg, and png files under 5mb')])
    submit = SubmitField('Post')
'''

