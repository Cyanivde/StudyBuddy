from flask import render_template, request
from flask_login import current_user
from app import db
from app.models import ResourceToUser, Resource


def _update_resource_to_user():
    resource_id = request.get_json()['resource_id']
    val = request.get_json()['val']
    ilike = request.get_json()['ilike']

    if current_user.is_authenticated:
        count = db.session.query(ResourceToUser).filter_by(
            user_id=current_user.user_id, resource_id=resource_id).count()

        if count == 0:
            resource_to_user = ResourceToUser(
                user_id=current_user.user_id, resource_id=resource_id)
            db.session.add(resource_to_user)
        db.session.commit()
        if val:
            ResourceToUser.query.filter_by(user_id=current_user.user_id, resource_id=resource_id).update({'done': val})
        if ilike is not None:
            ResourceToUser.query.filter_by(user_id=current_user.user_id, resource_id=resource_id).update({'like': ilike})

            if ilike:
                Resource.query.filter_by(resource_id=resource_id).update({'likes': Resource.likes + 1})
            else:
                Resource.query.filter_by(resource_id=resource_id).update({'likes': Resource.likes - 1})

        db.session.commit()

    return render_template("index.html", title='Home Page')
