from flask import flash, redirect, render_template, url_for
from flask_login import login_user

from app import db
from app.forms import ResetPasswordForm
from app.models import User


def _reset_password(token):
    user = User.verify_reset_password_token(token)
    if not user:
        flash("הקישור אינו תקין. ייתכן שעבר יותר מדי זמן, נסו שנית",
              category="error")
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('form.html', title="איפוס סיסמה", form=form)

    # Form was submitted with valid input
    else:
        user.set_password(form.password.data)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
