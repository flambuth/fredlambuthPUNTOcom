from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length


class CourseForm(FlaskForm):
    search_term = StringField('Search: ', validators=[InputRequired(),
                                             Length(min=1, max=100)])
    description = TextAreaField('Course Description',
                                validators=[InputRequired(),
                                            Length(max=200)])
    price = IntegerField('Price', validators=[InputRequired()])