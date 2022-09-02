from flask import redirect, render_template, url_for
from app.forms import UpdateResourceForm
from app.utils import _fetch_subject_list, _fetch_resource_df, _update_form_according_to_resource, _update_resource_according_to_form, _insert_resource_according_to_form


def _update_resource(course_id, is_existing_resource, resource_id=None):
    form = UpdateResourceForm()

    form.subject.choices = _fetch_subject_list()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            form = _update_form_according_to_resource(form, resource)

        return render_template('updateresource.html', form=form, is_existing_resource=is_existing_resource)

    # Form was submitted with valid input
    if form.validate_on_submit():
        if is_existing_resource:
            resource_df = _fetch_resource_df(resource_id)
            resource = resource_df.iloc[0]
            _update_resource_according_to_form(resource, form)

        else:
            _insert_resource_according_to_form(form, course_id)

        return redirect(url_for('course', course_id=course_id))
