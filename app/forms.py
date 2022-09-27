
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
            ('2023-01 חורף תשפ"ג', '2023-01 חורף תשפ"ג'),
            ('2022-03 קיץ תשפ"ב', '2022-03 קיץ תשפ"ב'),
            ('2022-02 אביב תשפ"ב', '2022-02 אביב תשפ"ב'),
            ('2022-01 חורף תשפ"ב', '2022-01 חורף תשפ"ב'),
            ('2021-03 קיץ תשפ"א', '2021-03 קיץ תשפ"א'),
            ('2021-02 אביב תשפ"א', '2021-02 אביב תשפ"א'),
            ('2021-01 חורף תשפ"א', '2021-01 חורף תשפ"א'),
            ('2020-03 קיץ תש"פ', '2020-03 קיץ תש"פ'),
            ('2020-02 אביב תש"פ', '2020-02 אביב תש"פ'),
            ('2020-01 חורף תש"פ', '2020-01 חורף תש"פ'),
            ('2019-03 קיץ תשע"ט', '2019-03 קיץ תשע"ט'),
            ('2019-02 אביב תשע"ט', '2019-02 אביב תשע"ט'),
            ('2019-01 חורף תשע"ט', '2019-01 חורף תשע"ט'),
            ('2018-03 קיץ תשע"ח', '2018-03 קיץ תשע"ח'),
            ('2018-02 אביב תשע"ח', '2018-02 אביב תשע"ח'),
            ('2018-01 חורף תשע"ח', '2018-01 חורף תשע"ח'),
            ('2017-03 קיץ תשע"ז', '2017-03 קיץ תשע"ז'),
            ('2017-02 אביב תשע"ז', '2017-02 אביב תשע"ז'),
            ('2017-01 חורף תשע"ז', '2017-01 חורף תשע"ז'),
            ('2016-03 קיץ תשע"ו', '2016-03 קיץ תשע"ו'),
            ('2016-02 אביב תשע"ו', '2016-02 אביב תשע"ו'),
            ('2016-01 חורף תשע"ו', '2016-01 חורף תשע"ו'),
            ('2015-03 קיץ תשע"ה', '2015-03 קיץ תשע"ה'),
            ('2015-02 אביב תשע"ה', '2015-02 אביב תשע"ה'),
            ('2015-01 חורף תשע"ה', '2015-01 חורף תשע"ה'),
            ('2014-03 קיץ תשע"ד', '2014-03 קיץ תשע"ד'),
            ('2014-02 אביב תשע"ד', '2014-02 אביב תשע"ד'),
            ('2014-01 חורף תשע"ד', '2014-01 חורף תשע"ד'),
            ('2013-03 קיץ תשע"ג', '2013-03 קיץ תשע"ג'),
            ('2013-02 אביב תשע"ג', '2013-02 אביב תשע"ג'),
            ('2013-01 חורף תשע"ג', '2013-01 חורף תשע"ג'),
            ('2012-03 קיץ תשע"ב', '2012-03 קיץ תשע"ב'),
            ('2012-02 אביב תשע"ב', '2012-02 אביב תשע"ב'),
            ('2012-01 חורף תשע"ב', '2012-01 חורף תשע"ב'),
            ('2011-03 קיץ תשע"א', '2011-03 קיץ תשע"א'),
            ('2011-02 אביב תשע"א', '2011-02 אביב תשע"א'),
            ('2011-01 חורף תשע"א', '2011-01 חורף תשע"א'),
            ('2010-03 קיץ תש"ע', '2010-03 קיץ תש"ע'),
            ('2010-02 אביב תש"ע', '2010-02 אביב תש"ע'),
            ('2010-01 חורף תש"ע', '2010-01 חורף תש"ע'),
            ('2009-03 קיץ תשס"ט', '2009-03 קיץ תשס"ט'),
            ('2009-02 אביב תשס"ט', '2009-02 אביב תשס"ט'),
            ('2009-01 חורף תשס"ט', '2009-01 חורף תשס"ט'),
            ('2008-03 קיץ תשס"ח', '2008-03 קיץ תשס"ח'),
            ('2008-02 אביב תשס"ח', '2008-02 אביב תשס"ח'),
            ('2008-01 חורף תשס"ח', '2008-01 חורף תשס"ח'),
            ('2007-03 קיץ תשס"ז', '2007-03 קיץ תשס"ז'),
            ('2007-02 אביב תשס"ז', '2007-02 אביב תשס"ז'),
            ('2007-01 חורף תשס"ז', '2007-01 חורף תשס"ז'),
            ('2006-03 קיץ תשס"ו', '2006-03 קיץ תשס"ו'),
            ('2006-02 אביב תשס"ו', '2006-02 אביב תשס"ו'),
            ('2006-01 חורף תשס"ו', '2006-01 חורף תשס"ו'),
            ('2005-03 קיץ תשס"ה', '2005-03 קיץ תשס"ה'),
            ('2005-02 אביב תשס"ה', '2005-02 אביב תשס"ה'),
            ('2005-01 חורף תשס"ה', '2005-01 חורף תשס"ה'),
            ('2004-03 קיץ תשס"ד', '2004-03 קיץ תשס"ד'),
            ('2004-02 אביב תשס"ד', '2004-02 אביב תשס"ד'),
            ('2004-01 חורף תשס"ד', '2004-01 חורף תשס"ד'),
            ('2003-03 קיץ תשס"ג', '2003-03 קיץ תשס"ג'),
            ('2003-02 אביב תשס"ג', '2003-02 אביב תשס"ג'),
            ('2003-01 חורף תשס"ג', '2003-01 חורף תשס"ג'),
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
