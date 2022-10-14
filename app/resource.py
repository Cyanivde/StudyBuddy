from flask import render_template
from app.utils import _fetch_resource_df, _fetch_course


def _resource(institute, institute_course_id, resource_id):
    resource_df = _fetch_resource_df(resource_id)

    resource = resource_df.iloc[0]
    course = _fetch_course(int(resource.course_id))
    return render_template('resource.html', resource=resource, course=course)
