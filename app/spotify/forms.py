from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class CourseForm(FlaskForm):
    search_term = StringField('Search: ', validators=[InputRequired(),
                                             Length(min=1, max=100)])