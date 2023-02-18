from flask import redirect, render_template, url_for

from app.forms import UpdateResourceForm
from app.utils import (_fetch_creator_list, _fetch_resources,
                       _fetch_subject_list, _insert_resource_according_to_form,
                       _update_form_according_to_resource,
                       _update_resource_according_to_form)


def _update_resource(course_institute,
                     course_institute_id,
                     is_existing_resource,
                     resource_id=None):
    title = ""
    if is_existing_resource:
        title += "יצירת "
    else:
        title += "עריכת "
    title += "חומר לימוד"

    form = UpdateResourceForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        if is_existing_resource:
            resource = _fetch_resources(resource_id=resource_id,
                                        should_enrich=False
                                        ).iloc[0]

            form = _update_form_according_to_resource(form, resource)

        return render_template('update_resource.html',
                               title=title,
                               course_institute=course_institute,
                               course_institute_id=course_institute_id,
                               form=form,
                               is_existing_resource=is_existing_resource,
                               course_subjects=_fetch_subject_list(
                                   course_institute, course_institute_id),
                               course_creators=_fetch_creator_list(
                                   course_institute, course_institute_id))

    # Form was submitted with valid input
    if form.validate_on_submit():
        if is_existing_resource:
            resource_series = _fetch_resources(resource_id=resource_id,
                                               should_enrich=False
                                               ).iloc[0]
            _update_resource_according_to_form(resource_series, form)

        else:
            _insert_resource_according_to_form(form,
                                               course_institute,
                                               course_institute_id)

        return redirect(url_for('course',
                                course_institute=course_institute,
                                course_institute_id=course_institute_id,
                                tab=form.type.data + 's'))
