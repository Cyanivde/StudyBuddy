from flask import render_template

from app.utils import _fetch_courses


def _index():
    return render_template('index2.html', courses=_fetch_courses())
