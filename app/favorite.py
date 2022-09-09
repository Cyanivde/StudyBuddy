from flask import redirect, url_for
from flask_login import logout_user
from utils import _get_user
from app import db

def favorite(course_id, favorite_status):
    user = _get_user()
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('index'))
