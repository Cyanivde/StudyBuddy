from flask import redirect, url_for
from flask_login import logout_user


def _logout():
    logout_user()
    return redirect(url_for('index'))
