from flask import render_template, abort
from app.utils import _fetch_courses, _fetch_resources


def _course(course_institute, course_institute_id, tab):
    if tab not in ["lessons", "exercises", "exams", "others"]:
        abort(404)

    course = _fetch_courses(course_institute, course_institute_id)

    if course.empty:
        abort(404)

    course = course.iloc[0]

    resources_df = _fetch_resources(course_institute, course_institute_id, tab)

    return render_template('course.html', course=course, resources=resources_df, tab=tab)
