
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
            ('חורף תשפ"ג', 'חורף תשפ"ג'),
            ('קיץ תשפ"ב', 'קיץ תשפ"ב'),
            ('אביב תשפ"ב', 'אביב תשפ"ב'),
            ('חורף תשפ"ב', 'חורף תשפ"ב'),
            ('קיץ תשפ"א', 'קיץ תשפ"א'),
            ('אביב תשפ"א', 'אביב תשפ"א'),
            ('חורף תשפ"א', 'חורף תשפ"א'),
            ('קיץ תש"פ', 'קיץ תש"פ'),
            ('אביב תש"פ', 'אביב תש"פ'),
            ('חורף תש"פ', 'חורף תש"פ'),
            ('קיץ תשע"ט', 'קיץ תשע"ט'),
            ('אביב תשע"ט', 'אביב תשע"ט'),
            ('חורף תשע"ט', 'חורף תשע"ט'),
            ('קיץ תשע"ח', 'קיץ תשע"ח'),
            ('אביב תשע"ח', 'אביב תשע"ח'),
            ('חורף תשע"ח', 'חורף תשע"ח'),
            ('קיץ תשע"ז', 'קיץ תשע"ז'),
            ('אביב תשע"ז', 'אביב תשע"ז'),
            ('חורף תשע"ז', 'חורף תשע"ז'),
            ('קיץ תשע"ו', 'קיץ תשע"ו'),
            ('אביב תשע"ו', 'אביב תשע"ו'),
            ('חורף תשע"ו', 'חורף תשע"ו'),
            ('קיץ תשע"ה', 'קיץ תשע"ה'),
            ('אביב תשע"ה', 'אביב תשע"ה'),
            ('חורף תשע"ה', 'חורף תשע"ה'),
            ('קיץ תשע"ד', 'קיץ תשע"ד'),
            ('אביב תשע"ד', 'אביב תשע"ד'),
            ('חורף תשע"ד', 'חורף תשע"ד'),
            ('קיץ תשע"ג', 'קיץ תשע"ג'),
            ('אביב תשע"ג', 'אביב תשע"ג'),
            ('חורף תשע"ג', 'חורף תשע"ג'),
            ('קיץ תשע"ב', 'קיץ תשע"ב'),
            ('אביב תשע"ב', 'אביב תשע"ב'),
            ('חורף תשע"ב', 'חורף תשע"ב'),
            ('קיץ תשע"א', 'קיץ תשע"א'),
            ('אביב תשע"א', 'אביב תשע"א'),
            ('חורף תשע"א', 'חורף תשע"א'),
            ('קיץ תש"ע', 'קיץ תש"ע'),
            ('אביב תש"ע', 'אביב תש"ע'),
            ('חורף תש"ע', 'חורף תש"ע'),
            ('קיץ תשס"ט', 'קיץ תשס"ט'),
            ('אביב תשס"ט', 'אביב תשס"ט'),
            ('חורף תשס"ט', 'חורף תשס"ט'),
            ('קיץ תשס"ח', 'קיץ תשס"ח'),
            ('אביב תשס"ח', 'אביב תשס"ח'),
            ('חורף תשס"ח', 'חורף תשס"ח'),
            ('קיץ תשס"ז', 'קיץ תשס"ז'),
            ('אביב תשס"ז', 'אביב תשס"ז'),
            ('חורף תשס"ז', 'חורף תשס"ז'),
            ('קיץ תשס"ו', 'קיץ תשס"ו'),
            ('אביב תשס"ו', 'אביב תשס"ו'),
            ('חורף תשס"ו', 'חורף תשס"ו'),
            ('קיץ תשס"ה', 'קיץ תשס"ה'),
            ('אביב תשס"ה', 'אביב תשס"ה'),
            ('חורף תשס"ה', 'חורף תשס"ה'),
            ('קיץ תשס"ד', 'קיץ תשס"ד'),
            ('אביב תשס"ד', 'אביב תשס"ד'),
            ('חורף תשס"ד', 'חורף תשס"ד'),
            ('קיץ תשס"ג', 'קיץ תשס"ג'),
            ('אביב תשס"ג', 'אביב תשס"ג'),
            ('חורף תשס"ג', 'חורף תשס"ג'),
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
