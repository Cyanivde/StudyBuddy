from flask import redirect, render_template, url_for
from flask_login import current_user, login_user


from app import db
from app.forms import RegistrationForm
from app.models import User


def _register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    # Form was submitted with valid input
    else:
        user = User(username=form.username.data.lower(), email=form.email.data.lower(), is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
