from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, DecimalField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class OrderForm(FlaskForm):
    submit = SubmitField('طلب')


class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class DishReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class RestaurantForm(FlaskForm):
    name = StringField('اسم المطعم', validators=[DataRequired()])
    address = StringField('العنوان', validators=[DataRequired()])
    image = FileField('صورة المطعم', validators=[FileAllowed(['jpg', 'png'], 'فقط ملفات jpg و png مسموحة')])

class MenuItemForm(FlaskForm):
    name = StringField('اسم الطبق', validators=[DataRequired()])
    price = DecimalField('السعر', validators=[DataRequired()])
    image = FileField('صورة الطبق', validators=[FileAllowed(['jpg', 'png'], 'فقط ملفات jpg و png مسموحة')])
