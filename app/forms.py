
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp
from app.constants.dates import SEMESTER_WEEK
from app.models import User

ERR_EMPTY = "לא ניתן להשאיר ריק"


def strip_whitespace(s):
    if isinstance(s, str):
        s = s.strip()
    return s


class CourseResourcesForm(FlaskForm):
    resources = TextAreaField('חומרי הקורס')
    archive = TextAreaField('ארכיון חומרים')
    exams = TextAreaField('מבחנים')
    submit = SubmitField('שמירה')


class UpdateResourceForm(FlaskForm):
    header = StringField('כותרת')
    rname = StringField('שם')
    rname_part = StringField('חלק')
    week = SelectField('שבוע', choices=SEMESTER_WEEK, validate_choice=False)
    tab = SelectField(
        'לשונית', choices=[('semester', 'סמסטר'), ('exams', 'מבחנים'), ('archive', 'ארכיון')], validate_choice=False, description="שבוע")
    link = StringField('קישור')
    solution = StringField('פתרון')
    recording = StringField('הקלטה')
    subject = SelectMultipleField('נושא', validate_choice=False)
    textdump = TextAreaField('העתקה של הטקסט')
    submit = SubmitField('שמירה')


class LoginForm(FlaskForm):
    username = StringField('שם משתמש', filters=[strip_whitespace], validators=[
                           DataRequired(message=ERR_EMPTY)])
    password = PasswordField('סיסמה', validators=[
        DataRequired(message=ERR_EMPTY)])
    remember_me = BooleanField('זכור אותי')
    submit = SubmitField('התחברות')


class RegistrationForm(FlaskForm):
    username = StringField('username', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_EMPTY), Regexp(r"^\w{5,20}$", message=".שם המשתמש חייב להכיל 5-20 תווים: אותיות, ספרות או קו תחתון")])
    email = StringField('email', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_EMPTY),  Email(message="כתובת המייל אינה תקינה.")])
    password = PasswordField('password', validators=[
        DataRequired(message=ERR_EMPTY), Regexp('^(?=.*?[A-Za-z#?!@$%^&*-])(?=.*?[0-9]).{8,}$', message="הסיסמה חייבת להכיל 8 תווים לפחות, מהם לפחות אות אחת וספרה אחת.")])
    password2 = PasswordField(
        'confirm password', validators=[DataRequired(ERR_EMPTY), EqualTo('password')])
    submit = SubmitField('הרשמה')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('שם המשתמש כבר נמצא בשימוש.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('כתובת המייל כבר נמצאת בשימוש.')
