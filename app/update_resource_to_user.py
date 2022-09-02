from flask import render_template, request
from flask_login import current_user
from app import db
from app.models import ResourceToUser


def _update_resource_to_user():
    resource_id = request.get_json()['resource_id']
    val = request.get_json()['val']

    if current_user.is_authenticated:
        db.session.query(ResourceToUser).filter_by(
            user_id=current_user.user_id, resource_id=resource_id).delete()

        resource_to_user = ResourceToUser(
            user_id=current_user.user_id, resource_id=resource_id, done=val)
        db.session.add(resource_to_user)
        db.session.commit()

    return render_template("index.html", title='Home Page')
