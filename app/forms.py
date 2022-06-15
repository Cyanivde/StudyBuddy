from curses import ERR
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp, Length

from app.models import User

ERR_USERNAME_EMPTY = "לא ניתן להזין שם משתמש ריק."
ERR_PASSWORD_EMPTY = "לא ניתן להזין סיסמה ריקה."
ERR_EMAIL_EMPTY = "לא ניתן להזין כתובת מייל ריקה."


def strip_whitespace(s):
    if isinstance(s, str):
        s = s.strip()
    return s


class SubjectsForm(FlaskForm):
    subjects = TextAreaField('עץ הנושאים')
    submit = SubmitField('שמירה')


class LoginForm(FlaskForm):
    username = StringField('שם משתמש', filters=[strip_whitespace], validators=[
                           DataRequired(message=ERR_USERNAME_EMPTY)])
    password = PasswordField('סיסמה', validators=[
        DataRequired(message=ERR_PASSWORD_EMPTY)])
    remember_me = BooleanField('זכור אותי')
    submit = SubmitField('התחברות')


class RegistrationForm(FlaskForm):
    username = StringField('שם משתמש', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_USERNAME_EMPTY), Regexp('^\w{5,20}$', message=".שם המשתמש חייב להכיל 5-20 תווים: אותיות, ספרות או קו תחתון")])
    email = StringField('כתובת מייל', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_EMAIL_EMPTY),  Email()])
    password = PasswordField('סיסמה', validators=[
        DataRequired(message=ERR_PASSWORD_EMPTY), Regexp('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', message="הסיסמה חייבת להכיל 8 תווים לפחות, מהם לפחות אות אחת וספרה אחת.")])
    password2 = PasswordField(
        'סיסמה', validators=[DataRequired(ERR_PASSWORD_EMPTY), EqualTo('סיסמה')])
    submit = SubmitField('הרשמה')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('שם המשתמש כבר נמצא בשימוש.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('כתובת המייל כבר נמצאת בשימוש.')
