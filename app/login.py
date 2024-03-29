from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user

from app.forms import LoginForm
from app.models import User


def _login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('form.html',
                               title="התחברות",
                               form=form,
                               additional_link=url_for('forgot_password'),
                               additional_link_label="שכחתי סיסמה")

    # Form was submitted with valid input
    else:
        user = User.query.filter(
            (User.username == form.usernameemail.data.lower()) |
            (User.email == form.usernameemail.data.lower())
        ).first()

        if user is None or not user.check_password(form.password.data):
            flash('פרטי ההתחברות שגויים', category='error')
            return redirect(url_for('login'))

        login_user(user, remember=True)
        return redirect(url_for('index'))
