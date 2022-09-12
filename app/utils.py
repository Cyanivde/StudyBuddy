from flask import abort
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import ResourceToCourse, Subject, Resource, Course, ResourceToUser
import pandas as pd
import json
import hashlib


def _fetch_resource_df(resource_id):
    resource_df = pd.read_sql(Resource.query.filter_by(resource_id=resource_id).statement, db.session.bind)

    if len(resource_df) == 0:
        abort(404)

    resource_to_course_df = pd.read_sql(ResourceToCourse.query.filter_by(resource_id=resource_id).statement, db.session.bind)

    if len(resource_to_course_df) == 0:
        abort(404)

    course_df = pd.read_sql(Course.query.filter(Course.course_id.in_(resource_to_course_df['course_id'])).statement, db.session.bind)

    merged_resource_df = pd.merge(left=resource_df, right=resource_to_course_df, on='resource_id')

    merged_resource_df = pd.merge(left=merged_resource_df, right=course_df, on='course_id')

    return merged_resource_df


def _fetch_subject_list():
    subject_names = [subject.subject_name for subject in Subject.query.all()]
    if subject_names is not None:
        subject_names.sort()

    return subject_names


def _update_form_according_to_resource(form, resource):
    form.link.data = resource.link
    form.solution.data = resource.solution
    form.recording.data = resource.recording
    form.subject.data = json.loads(resource.subject)
    return form


def _update_resource_according_to_form(resource, form):
    actual_resource = db.session.query(Resource).filter_by(resource_id=int(resource.resource_id)).first()

    actual_resource.link = form.link.data
    actual_resource.solution = form.solution.data
    actual_resource.recording = form.recording.data
    actual_resource.subject = json.dumps(form.subject.data)

    db.session.commit()
    db.session.refresh(actual_resource)


def _insert_resource_according_to_form(form, course_id):
    if not form.header.data:
        form.header.data = "ללא כותרת"

    if not form.rname_part.data:
        form.rname_part.data = None

    resource = Resource(link=form.link.data,
                        solution=form.solution.data,
                        recording=form.recording.data,
                        subject=json.dumps(form.subject.data))
    db.session.add(resource)
    db.session.commit()
    db.session.refresh(resource)

    same_tab_and_header_max = db.session.query(func.max(ResourceToCourse.order_in_tab)).filter_by(
        course_id=course_id, tab=form.tab.data, header=form.header.data).scalar()
    if not same_tab_and_header_max:
        same_tab_and_header_max = 0

    same_tab_count = ResourceToCourse.query.filter_by(course_id=course_id, tab=form.tab.data).count()

    new_resource_order_in_tab = same_tab_and_header_max + 1
    if new_resource_order_in_tab == 1:
        new_resource_order_in_tab = same_tab_count + 1

    ResourceToCourse.query.filter(
        ResourceToCourse.order_in_tab >= new_resource_order_in_tab).filter_by(
        course_id=course_id, tab=form.tab.data).update({'order_in_tab': ResourceToCourse.order_in_tab + 1})

    resource_to_course = ResourceToCourse(course_id=course_id, resource_id=resource.resource_id, header=form.header.data,
                                          rname=form.rname.data, rname_part=form.rname_part.data, tab=form.tab.data, order_in_tab=new_resource_order_in_tab)
    db.session.add(resource_to_course)
    db.session.commit()


def _get_subjects(resources_df):
    list_of_lists = [
        resource[1].subject for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _filter_resources(resources_extended_df, subject):
    if subject:
        resources_extended_df['show'] = resources_extended_df['subject'].apply(
            lambda x: any([subj in x for subj in subject]))
    else:
        resources_extended_df['show'] = True

    resources_extended_df = resources_extended_df[resources_extended_df['show']]

    return resources_extended_df


def _fetch_resources(course_id, tab):
    resource_to_course_df = pd.read_sql(ResourceToCourse.query.filter_by(
        course_id=course_id, tab=tab).statement, db.session.bind)

    if len(resource_to_course_df) == 0:
        return pd.DataFrame()

    resource_to_course_df.drop('id', axis=1, inplace=True)
    resource_to_course_df.drop('course_id', axis=1, inplace=True)
    resource_to_course_df.sort_values('order_in_tab', inplace=True)
    resource_ids = set(resource_to_course_df['resource_id'])

    resources_df = pd.read_sql(Resource.query.filter(
        Resource.resource_id.in_(resource_ids)).statement, db.session.bind)

    resources_extended_df = resource_to_course_df
    if len(resources_df) > 0:
        resource_to_course_df.drop('tab', axis=1, inplace=True)
        resources_extended_df = pd.merge(how='right', left=resources_df, right=resource_to_course_df,
                                         on="resource_id")

    if current_user.is_authenticated:
        resource_to_user = pd.read_sql(ResourceToUser.query.filter_by(
            user_id=current_user.user_id).statement, db.session.bind)

        if len(resource_to_user) > 0:
            resource_to_user.drop('id', axis=1, inplace=True)
            resource_to_user.drop('user_id', axis=1, inplace=True)
            resources_extended_df = pd.merge(how='left',
                                             left=resources_extended_df, right=resource_to_user, on="resource_id")

    if 'subject' in resources_extended_df.keys():
        resources_extended_df['subject'] = resources_extended_df['subject'].apply(
            lambda x: _jsonload(x))

    resources_extended_df = resources_extended_df.fillna(0)
    return resources_extended_df


def _add_fake_rows(resources_extended_df):
    resources_extended_df['is_fake_row'] = False

    resources_with_folded_rows = pd.DataFrame()
    folded_row_names = set()

    for index, row in resources_extended_df.iterrows():
        folded_row_name = row['rname']
        if row['rname_part'] and folded_row_name not in folded_row_names:
            folded_row_names.add(folded_row_name)
            folded_row = dict(row)
            folded_row['is_fake_row'] = True
            if 'done' in resources_extended_df.columns:
                folded_row['done'] = resources_extended_df[resources_extended_df['rname']
                                                           == folded_row_name]['done'].min()
            folded_row['subject'] = set([item for sublist in resources_extended_df[resources_extended_df['rname']
                                                                                   == folded_row_name]['subject'] for item in sublist])
            resources_with_folded_rows = resources_with_folded_rows.append(
                folded_row, ignore_index=True)
        resources_with_folded_rows = resources_with_folded_rows.append(
            row, ignore_index=True)

    resources_with_folded_rows['name_md5'] = resources_with_folded_rows['rname'].apply(
        lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())
    return resources_with_folded_rows


def _jsonload(x):
    if isinstance(x, str):
        return json.loads(x)
    else:
        return ''


def _resources_to_textarea(df):
    return "\r\n".join(["{0} | {1} / {2} / {3}".format(
        resource.resource_id, resource.header, resource.rname, resource.rname_part or '') for index, resource in df.iterrows()])
