from curses import ERR
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp, Length

from app.models import User

ERR_USERNAME_EMPTY = "Username must not be empty."
ERR_PASSWORD_EMPTY = "Password must not be empty."
ERR_EMAIL_EMPTY = "Email must not be empty."


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(message=ERR_USERNAME_EMPTY)])
    password = PasswordField('Password', validators=[
        DataRequired(message=ERR_PASSWORD_EMPTY)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message=ERR_USERNAME_EMPTY), Regexp('^\w{5,20}$', message="Username must contain 5-20 letters, numbers or underscore.")])
    email = StringField('Email', validators=[
        DataRequired(message=ERR_EMAIL_EMPTY), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(message=ERR_PASSWORD_EMPTY), Regexp('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', message="Password must contain 8+ characters, of which at least one letter and one number.")])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(ERR_PASSWORD_EMPTY), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('Username is already in use.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Email address is already in use.')
