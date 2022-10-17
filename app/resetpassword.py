from flask import redirect, render_template, url_for
from flask_login import current_user, login_user


from app import db
from app.forms import ResetPasswordForm
from app.models import User


def _resetpassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('resetpassword.html', form=form)

    # Form was submitted with valid input
    else:
        user.set_password(form.password.data)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
