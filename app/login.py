from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_user
from sqlalchemy import true

from app.forms import LoginForm
from app.models import User


def _login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('login.html', title='Sign In', form=form)

    # Form was submitted with valid input
    else:
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('שם המשתמש או הסיסמה שגויים')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('index'))
