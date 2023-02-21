
from flask_wtf import FlaskForm
from wtforms import (BooleanField, FieldList, PasswordField, SelectField,
                     StringField, SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Regexp,
                                ValidationError)

from app.models import User
from app.utils import SEMESTERS_LIST, strip_whitespace

ERR_EMPTY = "לא ניתן להשאיר ריק"
ERR_INVALID_USERNAME = "שם המשתמש חייב להכיל 5-20 תווים"
ERR_INVALID_EMAIL = "כתובת המייל אינה תקינה"
ERR_INVALID_PASSWORD = "הסיסמה חייבת להכיל 8 תווים לפחות, עם אות אחת וספרה אחת"
ERR_USERNAME_TAKEN = "שם המשתמש כבר נמצא בשימוש"
ERR_EMAIL_TAKEN = "כתובת המייל כבר נמצאת בשימוש"
ERR_PASSWORD_MATCH = "הסיסמאות אינן תואמות"
ERR_NOT_ALLOWED_SITE = "הקישור אינו עומד בדרישות"
USERNAME_REGEX = r"^\w{5,20}$"
PASSWORD_REGEX = "^(?=.*?[A-Za-z#?!@$%^&*-])(?=.*?[0-9]).{8,}$"
ALLOWED_SITES_REGEX = r"^(?!.*grades\.cs|.*moodle2223\.technion.|.*moodle2222\.technion.).*$"


class RegistrationForm(FlaskForm):
    username = StringField('שם משתמש',
                           filters=[strip_whitespace],
                           validators=[DataRequired(message=ERR_EMPTY),
                                       Regexp(USERNAME_REGEX,
                                              message=ERR_INVALID_USERNAME)])

    email = StringField('כתובת מייל',
                        filters=[strip_whitespace],
                        validators=[DataRequired(message=ERR_EMPTY),
                                    Email(message=ERR_INVALID_EMAIL)])

    password = PasswordField('סיסמה',
                             validators=[DataRequired(message=ERR_EMPTY),
                                         Regexp(PASSWORD_REGEX,
                                                message=ERR_INVALID_PASSWORD)])

    password2 = PasswordField('אימות סיסמה',
                              validators=[DataRequired(ERR_EMPTY),
                                          EqualTo('password',
                                                  message=ERR_PASSWORD_MATCH)])

    submit = SubmitField('הרשמה')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError(ERR_USERNAME_TAKEN)

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError(ERR_EMAIL_TAKEN)


class LoginForm(FlaskForm):
    usernameemail = StringField('שם משתמש או כתובת מייל',
                                filters=[strip_whitespace],
                                validators=[DataRequired(message=ERR_EMPTY)])

    password = PasswordField('סיסמה',
                             validators=[DataRequired(message=ERR_EMPTY)])

    submit = SubmitField('התחברות')


class ForgotPasswordForm(FlaskForm):
    usernameemail = StringField('שם משתמש או כתובת מייל',
                                filters=[strip_whitespace],
                                validators=[DataRequired(message=ERR_EMPTY)])

    submit = SubmitField('שליחה')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('סיסמה חדשה',
                             validators=[DataRequired(message=ERR_EMPTY),
                                         Regexp(PASSWORD_REGEX,
                                                message=ERR_INVALID_PASSWORD)])

    password2 = PasswordField('אימות סיסמה חדשה',
                              validators=[DataRequired(ERR_EMPTY),
                                          EqualTo('password')])

    submit = SubmitField('שמירה')


class UpdateResourceForm(FlaskForm):
    semester = SelectField('סמסטר',
                           choices=SEMESTERS_LIST)

    type = SelectField('סוג',
                       choices=[
                           ('lesson', 'שיעור (הרצאה/תרגול/סדנה)'),
                           ('exercise_full', 'תרגיל בית'),
                           ('exercise', 'שאלה מתרגיל בית'),
                           ('exam_full', 'מבחן'),
                           ('exam', 'שאלה ממבחן'),
                           ('other', 'אחר (למשל סיכום אישי)')
                       ])

    folder = StringField('תיקייה')

    display_name = StringField('שם תצוגה')

    questions_count = SelectField('כמה שאלות יש?', choices=range(1, 26))

    link = StringField('קישור',
                       validators=[Regexp(ALLOWED_SITES_REGEX,
                                          message=ERR_NOT_ALLOWED_SITE)])

    solution = StringField('קישור לפתרון',
                           validators=[Regexp(ALLOWED_SITES_REGEX,
                                              message=ERR_NOT_ALLOWED_SITE)])

    recording = FieldList(StringField(),
                          'קישורים להקלטות',
                          min_entries=5)

    recording_comment = FieldList(StringField(),
                                  'הערות להקלטות',
                                  min_entries=5)

    subject = StringField('נושאים (מופרדים בפסיק)')

    creator = StringField('יוצרים (מופרדים בפסיק)')

    is_out_of_date = BooleanField('כבר לא בחומר')

    is_solution_partial = BooleanField('הפתרון חלקי')

    is_in_recycle_bin = BooleanField('לשים בסל המיחזור')

    submit = SubmitField('שמירה')
