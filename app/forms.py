
from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Regexp,
                                ValidationError)

from app.models import User
from app.utils import strip_whitespace

ERR_EMPTY = "לא ניתן להשאיר ריק"
ERR_INVALID_USERNAME = "שם המשתמש חייב להכיל 5-20 תווים"
ERR_INVALID_EMAIL = "כתובת המייל אינה תקינה"
ERR_INVALID_PASSWORD = "הסיסמה חייבת להכיל 8 תווים לפחות, עם אות אחת וספרה אחת"
ERR_USERNAME_TAKEN = "שם המשתמש כבר נמצא בשימוש"
ERR_EMAIL_TAKEN = "כתובת המייל כבר נמצאת בשימוש"
USERNAME_REGEX = r"^\w{5,20}$"
PASSWORD_REGEX = "^(?=.*?[A-Za-z#?!@$%^&*-])(?=.*?[0-9]).{8,}$"


class RegistrationForm(FlaskForm):
    username = StringField('username',
                           filters=[strip_whitespace],
                           validators=[DataRequired(message=ERR_EMPTY),
                                       Regexp(USERNAME_REGEX,
                                              message=ERR_INVALID_USERNAME)])

    email = StringField('email',
                        filters=[strip_whitespace],
                        validators=[DataRequired(message=ERR_EMPTY),
                                    Email(message=ERR_INVALID_EMAIL)])

    password = PasswordField('password',
                             validators=[DataRequired(message=ERR_EMPTY),
                                         Regexp(PASSWORD_REGEX,
                                                message=ERR_INVALID_PASSWORD)])

    password2 = PasswordField('confirm password',
                              validators=[DataRequired(ERR_EMPTY),
                                          EqualTo('password')])

    submit = SubmitField('הרשמה')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError()

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError()


class UpdateResourceForm(FlaskForm):
    type = SelectField('סוג',
                       choices=[
                           ('lecture', 'שיעור (הרצאה/תרגול/סדנה)'),
                           ('exercise_full', 'תרגיל בית'),
                           ('exercise', 'שאלה מתרגיל בית'),
                           ('exam_full', 'מבחן'),
                           ('exam', 'שאלה ממבחן'),
                           ('other', 'אחר (למשל סיכום אישי)')])
    display_name = StringField('שם תצוגה')
    questions_count = SelectField('כמה שאלות יש?', choices=range(1, 26))
    grouping = StringField('תיקייה')

    link = StringField('קישור', validators=[Regexp(
        r"^.*(sharepoint|github)\.com.*|\w{0}$", message="הקישור אינו תקין")])
    semester = SelectField(
        'סמסטר', choices=[
            ('חורף 2022-2023', 'חורף 2022-2023'),
            ('קיץ 2022', 'קיץ 2022'),
            ('אביב 2022', 'אביב 2022'),
            ('חורף 2021-2022', 'חורף 2021-2022'),
            ('קיץ 2021', 'קיץ 2021'),
            ('אביב 2021', 'אביב 2021'),
            ('חורף 2020-2021', 'חורף 2020-2021'),
            ('קיץ 2020', 'קיץ 2020'),
            ('אביב 2020', 'אביב 2020'),
            ('חורף 2019-2020', 'חורף 2019-2020'),
            ('קיץ 2019', 'קיץ 2019'),
            ('אביב 2019', 'אביב 2019'),
            ('חורף 2018-2019', 'חורף 2018-2019'),
            ('קיץ 2018', 'קיץ 2018'),
            ('אביב 2018', 'אביב 2018'),
            ('חורף 2017-2018', 'חורף 2017-2018'),
            ('קיץ 2017', 'קיץ 2017'),
            ('אביב 2017', 'אביב 2017'),
            ('חורף 2016-2017', 'חורף 2016-2017'),
            ('קיץ 2016', 'קיץ 2016'),
            ('אביב 2016', 'אביב 2016'),
            ('חורף 2015-2016', 'חורף 2015-2016'),
            ('קיץ 2015', 'קיץ 2015'),
            ('אביב 2015', 'אביב 2015'),
            ('חורף 2014-2015', 'חורף 2014-2015'),
            ('קיץ 2014', 'קיץ 2014'),
            ('אביב 2014', 'אביב 2014'),
            ('חורף 2013-2014', 'חורף 2013-2014'),
            ('קיץ 2013', 'קיץ 2013'),
            ('אביב 2013', 'אביב 2013'),
            ('חורף 2012-2013', 'חורף 2012-2013'),
            ('קיץ 2012', 'קיץ 2012'),
            ('אביב 2012', 'אביב 2012'),
            ('חורף 2011-2012', 'חורף 2011-2012'),
            ('קיץ 2011', 'קיץ 2011'),
            ('אביב 2011', 'אביב 2011'),
            ('חורף 2010-2011', 'חורף 2010-2011'),
            ('קיץ 2010', 'קיץ 2010'),
            ('אביב 2010', 'אביב 2010'),
            ('חורף 2009-2010', 'חורף 2009-2010'),
            ('קיץ 2009', 'קיץ 2009'),
            ('אביב 2009', 'אביב 2009'),
            ('חורף 2008-2009', 'חורף 2008-2009'),
            ('קיץ 2008', 'קיץ 2008'),
            ('אביב 2008', 'אביב 2008'),
            ('חורף 2007-2008', 'חורף 2007-2008'),
            ('קיץ 2007', 'קיץ 2007'),
            ('אביב 2007', 'אביב 2007'),
            ('חורף 2006-2007', 'חורף 2006-2007'),
            ('קיץ 2006', 'קיץ 2006'),
            ('אביב 2006', 'אביב 2006'),
            ('חורף 2005-2006', 'חורף 2005-2006'),
            ('קיץ 2005', 'קיץ 2005'),
            ('אביב 2005', 'אביב 2005'),
            ('חורף 2004-2005', 'חורף 2004-2005'),
            ('קיץ 2004', 'קיץ 2004'),
            ('אביב 2004', 'אביב 2004'),
            ('חורף 2003-2004', 'חורף 2003-2004'),
            ('קיץ 2003', 'קיץ 2003'),
            ('אביב 2003', 'אביב 2003'),
            ('חורף 2002-2003', 'חורף 2002-2003'),
            ('קיץ 2002', 'קיץ 2002'),
            ('אביב 2002', 'אביב 2002'),
            ('חורף 2001-2002', 'חורף 2001-2002'),
            ('קיץ 2001', 'קיץ 2001'),
            ('אביב 2001', 'אביב 2001'),
            ('חורף 2000-2001', 'חורף 2000-2001'),
            ('קיץ 2000', 'קיץ 2000'),
            ('אביב 2000', 'אביב 2000'),
        ],
        validate_choice=False)
    solution = StringField('קישור לפתרון', validators=[Regexp(
        r"^.*(sharepoint|github)\.com.*|\w{0}$", message="הקישור אינו תקין")])
    recording = StringField('קישורים להקלטות')
    recording2 = StringField('קישורים להקלטות')
    recording3 = StringField('קישורים להקלטות')
    recording4 = StringField('קישורים להקלטות')
    recording5 = StringField('קישורים להקלטות')
    recording_comment = StringField('הערה להקלטה')
    recording2_comment = StringField('הערה להקלטה')
    recording3_comment = StringField('הערה להקלטה')
    recording4_comment = StringField('הערה להקלטה')
    recording5_comment = StringField('הערה להקלטה')
    subject = StringField('נושאים (מופרדים בפסיק)')
    instructor = StringField('יוצרים (מופרדים בפסיק)')
    is_out_of_date = BooleanField('כבר לא בחומר')
    is_solution_partial = BooleanField('הפתרון חלקי')
    submit = SubmitField('שמירה')


class forgot_passwordForm(FlaskForm):
    usernameemail = StringField('שם משתמש או כתובת מייל', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_EMPTY)])
    submit = SubmitField('שליחה')


class LoginForm(FlaskForm):
    usernameemail = StringField('שם משתמש או כתובת מייל', filters=[strip_whitespace], validators=[
        DataRequired(message=ERR_EMPTY)])
    password = PasswordField('סיסמה', validators=[
        DataRequired(message=ERR_EMPTY)])
    remember_me = BooleanField('זכור אותי')
    submit = SubmitField('התחברות')


class reset_passwordForm(FlaskForm):
    password = PasswordField('password', validators=[
        DataRequired(message=ERR_EMPTY), Regexp('^(?=.*?[A-Za-z#?!@$%^&*-])(?=.*?[0-9]).{8,}$', message="הסיסמה חייבת להכיל 8 תווים לפחות, מהם לפחות אות אחת וספרה אחת.")])
    password2 = PasswordField(
        'confirm password', validators=[DataRequired(ERR_EMPTY), EqualTo('password')])
    submit = SubmitField('שמירה')
