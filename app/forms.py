
from sqlite3 import Date
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Regexp, Optional

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
    type = SelectField('סוג', choices=[
        (None, ''),
        ('lecture', 'הרצאה'),
        ('tutorial', 'תרגול'),
        ('workshop', 'סדנה'),
        ('exercise', 'תרגיל בית'),
        ('exam', 'מבחן'),
        ('other', 'אחר')])
    display_name = StringField('שם תצוגה')
    deadline_week = SelectField('שבוע בקורס', choices=[
        (None, ''),
        ('week1', 'שבוע 1'),
        ('week2', 'שבוע 2'),
        ('week3', 'שבוע 3'),
        ('week4', 'שבוע 4'),
        ('week5', 'שבוע 5'),
        ('week6', 'שבוע 6'),
        ('week7', 'שבוע 7'),
        ('week8', 'שבוע 8'),
        ('week9', 'שבוע 9'),
        ('week10', 'שבוע 10'),
        ('week11', 'שבוע 11'),
        ('week12', 'שבוע 12'),
        ('week13', 'שבוע 13'),
        ('presemester', 'לפני הסמסטר'),
        ('preexam', 'לקראת המבחן'),
        ('exactdate', 'תאריך מדויק')])
    deadline_date = DateField('תאריך דדליין', validators=(Optional(),))
    link = StringField('קישור')
    semester = SelectField(
        'סמסטר', choices=[
            ('חורף תשפג', 'חורף תשפג'),
            ('קיץ תשפב', 'קיץ תשפב'),
            ('אביב תשפב', 'אביב תשפב'),
            ('חורף תשפב', 'חורף תשפב'),
            ('קיץ תשפא', 'קיץ תשפא'),
            ('אביב תשפא', 'אביב תשפא'),
            ('חורף תשפא', 'חורף תשפא'),
            ('קיץ תשפ', 'קיץ תשפ'),
            ('אביב תשפ', 'אביב תשפ'),
            ('חורף תשפ', 'חורף תשפ'),
            ('קיץ תשעט', 'קיץ תשעט'),
            ('אביב תשעט', 'אביב תשעט'),
            ('חורף תשעט', 'חורף תשעט'),
            ('קיץ תשעח', 'קיץ תשעח'),
            ('אביב תשעח', 'אביב תשעח'),
            ('חורף תשעח', 'חורף תשעח'),
            ('קיץ תשעז', 'קיץ תשעז'),
            ('אביב תשעז', 'אביב תשעז'),
            ('חורף תשעז', 'חורף תשעז'),
            ('קיץ תשעו', 'קיץ תשעו'),
            ('אביב תשעו', 'אביב תשעו'),
            ('חורף תשעו', 'חורף תשעו'),
            ('קיץ תשעה', 'קיץ תשעה'),
            ('אביב תשעה', 'אביב תשעה'),
            ('חורף תשעה', 'חורף תשעה'),
            ('קיץ תשעד', 'קיץ תשעד'),
            ('אביב תשעד', 'אביב תשעד'),
            ('חורף תשעד', 'חורף תשעד'),
            ('קיץ תשעג', 'קיץ תשעג'),
            ('אביב תשעג', 'אביב תשעג'),
            ('חורף תשעג', 'חורף תשעג'),
            ('קיץ תשעב', 'קיץ תשעב'),
            ('אביב תשעב', 'אביב תשעב'),
            ('חורף תשעב', 'חורף תשעב'),
            ('קיץ תשעא', 'קיץ תשעא'),
            ('אביב תשעא', 'אביב תשעא'),
            ('חורף תשעא', 'חורף תשעא'),
            ('קיץ תשע', 'קיץ תשע'),
            ('אביב תשע', 'אביב תשע'),
            ('חורף תשע', 'חורף תשע'),
            ('קיץ תשסט', 'קיץ תשסט'),
            ('אביב תשסט', 'אביב תשסט'),
            ('חורף תשסט', 'חורף תשסט'),
            ('קיץ תשסח', 'קיץ תשסח'),
            ('אביב תשסח', 'אביב תשסח'),
            ('חורף תשסח', 'חורף תשסח'),
            ('קיץ תשסז', 'קיץ תשסז'),
            ('אביב תשסז', 'אביב תשסז'),
            ('חורף תשסז', 'חורף תשסז'),
            ('קיץ תשסו', 'קיץ תשסו'),
            ('אביב תשסו', 'אביב תשסו'),
            ('חורף תשסו', 'חורף תשסו'),
            ('קיץ תשסה', 'קיץ תשסה'),
            ('אביב תשסה', 'אביב תשסה'),
            ('חורף תשסה', 'חורף תשסה'),
            ('קיץ תשסד', 'קיץ תשסד'),
            ('אביב תשסד', 'אביב תשסד'),
            ('חורף תשסד', 'חורף תשסד'),
            ('קיץ תשסג', 'קיץ תשסג'),
            ('אביב תשסג', 'אביב תשסג'),
            ('חורף תשסג', 'חורף תשסג'),
        ],
        validate_choice=False)
    solution = StringField('קישור לפתרון')
    recording = StringField('קישור להקלטה')
    subject = SelectMultipleField('נושא', validate_choice=False)
    is_official = BooleanField('חומר רשמי מהסגל')
    is_out_of_date = BooleanField('כבר לא בחומר')
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
