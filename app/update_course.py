from flask import render_template
from app import app, db
from app.forms import CourseResourcesForm
from app.models import Course, Resource
from app.utils import _fetch_resources, _resources_to_textarea


@app.route('/updatecourse/<course_id>', methods=['GET', 'POST'])
def _update_course(course_id):
    course = Course.query.filter_by(course_id=course_id).first_or_404()

    form = CourseResourcesForm()

    resources_df = _fetch_resources(course_id, "semester")
    archive_df = _fetch_resources(course_id, "archive")
    exams_df = _fetch_resources(course_id, "exams")

    if not form.validate_on_submit():
        form.resources.data = _resources_to_textarea(resources_df)
        form.archive.data = _resources_to_textarea(archive_df)
        form.exams.data = _resources_to_textarea(exams_df)
        return render_template('updatecourse.html', form=form, course=course)

    else:
        resources = [(line.split(' | ')[0], line.split(' | ')[1].split(' / ')[0], line.split(' | ')[1].split(' / ')[1], line.split(' | ')[1].split(' / ')[2] or None)
                     for line in form.resources.data.split('\r\n') if ' ' in line]
        archive = [(line.split(' | ')[0], line.split(' | ')[1].split(' / ')[0], line.split(' | ')[1].split(' / ')[1], line.split(' | ')[1].split(' / ')[2] or None)
                   for line in form.archive.data.split('\r\n') if ' ' in line]
        exams = [(line.split(' | ')[0], line.split(' | ')[1].split(' / ')[0], line.split(' | ')[1].split(' / ')[1], line.split(' | ')[1].split(' / ')[2] or None)
                 for line in form.exams.data.split('\r\n') if ' ' in line]

        Resource.query.filter_by(course_id = course_id).update({'tab': 'archive'})

        order_in_tab = 1
        for resource in resources:
            Resource.query.filter_by(resource_id = resource[0]).update({'header': resource[1], 'rname':resource[2], 'rname_part': resource[3], 'tab':'semester', 'order_in_tab':order_in_tab})
            order_in_tab += 1

        order_in_tab = 1
        for resource in archive:
            Resource.query.filter_by(resource_id = resource[0]).update({'header': resource[1], 'rname':resource[2], 'rname_part': resource[3], 'tab':'archive', 'order_in_tab':order_in_tab})
            order_in_tab += 1

        order_in_tab = 1
        for resource in exams:
            Resource.query.filter_by(resource_id = resource[0]).update({'header': resource[1], 'rname':resource[2], 'rname_part': resource[3], 'tab':'exams', 'order_in_tab':order_in_tab})
            order_in_tab += 1

        db.session.commit()

        return render_template('updatecourse.html', form=form, course=course)
