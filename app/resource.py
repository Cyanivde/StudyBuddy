from flask import render_template
from app.utils import _fetch_resource_df


def _resource(institute, institute_course_id, resource_id):
    resource_df = _fetch_resource_df(resource_id)
    resource = resource_df.iloc[0]
    print(resource)
    return render_template('resource.html', resource=resource)
