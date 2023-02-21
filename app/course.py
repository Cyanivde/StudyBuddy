from flask import abort, render_template

from app.utils import (_enrich_resources, _fetch_courses, _fetch_creator_list,
                       _fetch_resources, _fetch_subject_list)


def _course(course_institute, course_institute_id, tab):
    if tab not in ["lessons", "exercises", "exams", "others", "recycle_bin"]:
        abort(404)

    course = _fetch_courses(course_institute, course_institute_id)

    if course.empty:
        abort(404)

    course = course.iloc[0]

    resources_df = _fetch_resources(course_institute, course_institute_id)
    enriched_resources_df = None
    if tab == "recycle_bin":
        enriched_resources_df = resources_df[
            resources_df['is_in_recycle_bin'] == True]
    else:
        enriched_resources_df = resources_df[
            (resources_df['is_in_recycle_bin'] == False) &
            (resources_df['type'] == tab[:-1])]

    enriched_resources_df = _enrich_resources(
        enriched_resources_df, course_institute_id, tab)

    return render_template('course.html',
                           course=course,
                           resources=enriched_resources_df,
                           tab=tab,
                           course_subjects=_fetch_subject_list(course_institute,
                                                               course_institute_id,
                                                               resources_df),
                           course_creators=_fetch_creator_list(course_institute,
                                                               course_institute_id,
                                                               resources_df))
