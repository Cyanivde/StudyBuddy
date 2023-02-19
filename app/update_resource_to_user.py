from flask import request
from flask_login import current_user

from app import db
from app.models import Resource, ResourceToUser


def _update_resource_to_user():
    resource_id = request.get_json()['resource_id']
    val = request.get_json()['val']
    ilike = request.get_json()['ilike']

    # this whole function is only relevant for authenticated users
    if current_user.is_authenticated:
        r_to_u = ResourceToUser.query.filter_by(user_id=current_user.user_id,
                                                resource_id=resource_id
                                                ).first()

        if not r_to_u:
            r_to_u = ResourceToUser(user_id=current_user.user_id,
                                    resource_id=resource_id)
            db.session.add(r_to_u)
            db.session.commit()

        # change to "done" value
        if val is not None:
            ResourceToUser.query.filter_by(user_id=current_user.user_id,
                                           resource_id=resource_id
                                           ).update({'done': val})

        # channge to "like" value
        if ilike is not None:
            ResourceToUser.query.filter_by(user_id=current_user.user_id,
                                           resource_id=resource_id
                                           ).update({'like': ilike})

            if ilike:
                Resource.query.filter_by(resource_id=resource_id
                                         ).update({'likes':
                                                   Resource.likes + 1})
            else:
                Resource.query.filter_by(resource_id=resource_id
                                         ).update({'likes':
                                                   Resource.likes - 1})

        db.session.commit()

    return ('', 204)
