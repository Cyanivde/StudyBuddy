from threading import Thread

from flask import flash, redirect, render_template, url_for
from flask_mail import Message

from app import app, mail
from app.forms import ForgotPasswordForm
from app.models import User


def _forgot_password():
    form = ForgotPasswordForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('form.html', title="שכחתי סיסמה", form=form)

    # Form was submitted with valid input
    else:
        user = User.query.filter(
            (User.username == form.usernameemail.data.lower()) |
            (User.email == form.usernameemail.data.lower())
        ).first()

        if user is None:
            flash('שם המשתמש או כתובת המייל לא קיימים במערכת',
                  category='error')

        if user:
            token = user.get_reset_password_token()
            send_email('[StudyBuddy] איפוס סיסמה',
                       sender="donotreply@studybuddy.co.il",
                       recipients=[user.email],
                       text_body=render_template('email/reset_password.txt',
                                                 user=user, token=token),
                       html_body=render_template('email/reset_password.html',
                                                 user=user, token=token))

            flash('הוראות נשלחו אליך למייל. כדאי לבדוק גם בתיקיית הספאם.')

        return redirect(url_for('forgot_password'))


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
