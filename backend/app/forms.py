from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import User, Category
from wtforms.fields import DateTimeLocalField
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')



class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    profile_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')



def category_query():
    return Category.query



class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')



class GigForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price ($)', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    travel_radius = StringField('Travel Radius (km)', validators=[DataRequired()])
    submit = SubmitField('Create Gig')
    category = QuerySelectField(
        'Category',
        query_factory=category_query,
        get_label='name',
        allow_blank=False
    )



class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')



class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('Send')



class BookingForm(FlaskForm):
    booking_date = DateTimeLocalField('Booking Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Book Now')



class SearchForm(FlaskForm):
    keyword = StringField('Keyword')
    category = QuerySelectField('Category', query_factory=category_query, get_label='name', allow_blank=True)
    location = StringField('Location')
    radius = IntegerField('Radius (km)', validators=[Optional()])
    submit = SubmitField('Search')



class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')



