import re
from flask import abort
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import Subject, Resource, Course, ResourceToUser
import pandas as pd
import json
import hashlib


def _fetch_resource_df(resource_id):
    resource_df = pd.read_sql(Resource.query.filter_by(resource_id=resource_id).statement, db.session.bind)

    if len(resource_df) == 0:
        abort(404)

    course_df = pd.read_sql(Course.query.filter(Course.course_id.in_(resource_df['course_id'])).statement, db.session.bind)

    merged_resource_df = pd.merge(left=resource_df, right=course_df, on='course_id')

    return merged_resource_df


def _fetch_subject_list():
    subject_names = [subject.subject_name for subject in Subject.query.all()]
    if subject_names is not None:
        subject_names.sort()

    return subject_names


def _fetch_course(course_id):
    return Course.query.filter_by(course_id=course_id)[0]


def _update_form_according_to_resource(form, resource):
    form.display_name.data = resource.display_name
    form.link.data = resource.link
    form.type.data = resource.type
    form.solution.data = resource.solution
    form.recording.data = resource.recording
    form.is_official.data = resource.is_official
    form.is_out_of_date.data = resource.is_out_of_date
    form.semester.data = resource.semester
    form.deadline_week.data = resource.deadline_week
    form.deadline_date.data = resource.deadline_date
    form.subject.data = json.loads(resource.subject)
    return form


def _update_resource_according_to_form(resource, form):
    actual_resource = db.session.query(Resource).filter_by(resource_id=int(resource.resource_id)).first()

    actual_resource.display_name = form.display_name.data
    actual_resource.type = form.type.data
    actual_resource.link = form.link.data
    actual_resource.solution = form.solution.data
    actual_resource.recording = form.recording.data
    actual_resource.is_official = form.is_official.data
    actual_resource.is_out_of_date = form.is_out_of_date.data
    actual_resource.deadline_week = form.deadline_week.data
    actual_resource.semester = form.semester.data
    actual_resource.deadline_date = _get_date_from_week(form.deadline_week.data, form.deadline_date.data)
    actual_resource.subject = json.dumps(form.subject.data)

    db.session.commit()
    db.session.refresh(actual_resource)


def _insert_resource_according_to_form(form, course_id):
    resource = Resource(display_name=form.display_name.data,
                        type=form.type.data,
                        link=form.link.data,
                        solution=form.solution.data,
                        recording=form.recording.data,
                        is_official=form.is_official.data,
                        is_out_of_date=form.is_out_of_date.data,
                        deadline_week=form.deadline_week.data,
                        deadline_date=_get_date_from_week(form.deadline_week.data, form.deadline_date.data),
                        semester=form.semester.data,
                        likes=0,
                        subject=json.dumps(form.subject.data),
                        course_id=course_id)
    db.session.add(resource)
    db.session.commit()


def _get_subjects(resources_df):
    list_of_lists = [
        resource[1].subject for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _fetch_resources(course_id, tab):
    resource_df = pd.read_sql(Resource.query.filter_by(
        course_id=course_id).statement, db.session.bind)

    if len(resource_df) == 0:
        return pd.DataFrame()

    if tab == 'semester':
        resource_df = resource_df[resource_df['is_official'] & (resource_df['semester'] == 'חורף תשפג') & (resource_df['type'] != 'exam')]
        resource_df.sort_values('display_name', inplace=True)
        resource_df.sort_values('deadline_date', inplace=True)
        resource_df['deadline_date'] = resource_df['deadline_date'].fillna('המבחן')
        resource_df.insert(0, 'main', resource_df['deadline_date'].apply(lambda x: 'עד ' + str(x)[:10]))

    if tab == 'exams':
        resource_df = resource_df[resource_df['is_official'] & (resource_df['type'] == 'exam')]
        resource_df.sort_values('display_name', inplace=True)
        resource_df.sort_values('semester', ascending=False, inplace=True)
        resource_df.insert(0, 'main', resource_df['semester'])

    if tab == 'archive':
        resource_df = resource_df[~resource_df['is_official'] | ((resource_df['type'] != 'exam') & (resource_df['semester'] != 'חורף תשפג'))]
        resource_df.sort_values('display_name', inplace=True)
        resource_df.insert(0, 'main', resource_df['semester'])
        resource_df.sort_values('likes', ascending=False, inplace=True)

    resources_extended_df = resource_df
    if current_user.is_authenticated:
        resource_to_user = pd.read_sql(ResourceToUser.query.filter_by(
            user_id=current_user.user_id).statement, db.session.bind)

        if len(resource_to_user) > 0:
            resource_to_user.drop('id', axis=1, inplace=True)
            resource_to_user.drop('user_id', axis=1, inplace=True)
            resources_extended_df = pd.merge(how='left',
                                             left=resource_df, right=resource_to_user, on="resource_id")

    if 'subject' in resources_extended_df.keys():
        resources_extended_df['subject'] = resources_extended_df['subject'].apply(
            lambda x: _jsonload(x))

    resources_extended_df = resources_extended_df.fillna(0)
    return resources_extended_df


def _jsonload(x):
    if isinstance(x, str):
        return json.loads(x)
    else:
        return ''


def _update_resource_discord_link(resource_id, discord_link):
    Resource.query.filter_by(resource_id=resource_id).update({'comments': discord_link})
    db.session.commit()


def _get_date_from_week(week, default_date):
    if week == "presemester":
        return "2022-10-23"
    if week == "week1":
        return "2022-10-30"
    if week == "week2":
        return "2022-11-07"
    if week == "week3":
        return "2022-11-14"
    if week == "week4":
        return "2022-11-21"
    if week == "week5":
        return "2022-11-28"
    if week == "week6":
        return "2022-12-05"
    if week == "week7":
        return "2022-12-12"
    if week == "week8":
        return "2022-12-25"
    if week == "week9":
        return "2023-01-01"
    if week == "week10":
        return "2023-01-08"
    if week == "week11":
        return "2023-01-15"
    if week == "week12":
        return "2023-01-22"
    if week == "week13":
        return "2023-01-29"
    if week == "preexam":
        return None
    else:
        return default_date
