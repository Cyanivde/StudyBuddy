from re import sub
from flask import abort
from flask_login import current_user
from app import db
from app.models import Subject, Resource, Course, ResourceToUser
import pandas as pd


def _fetch_resource_df(resource_id):
    resource_df = pd.DataFrame([vars(s) for s in pd.Series(Resource.query.filter_by(
        resource_id=resource_id).all(), dtype=object)])

    if len(resource_df) == 0:
        abort(404)

    course_df = pd.DataFrame([vars(s) for s in pd.Series(Course.query.filter(
        Course.course_id.in_(resource_df['course_id'])).all(), dtype=object)])

    merged_resource_df = pd.merge(left=resource_df, right=course_df, on='course_id')

    return merged_resource_df


def _fetch_subject_list(course_id):
    resource_df = pd.DataFrame([vars(s) for s in pd.Series(Resource.query.filter_by(
        course_id=course_id).all(), dtype=object)])

    resource_df['subject'] = resource_df['subject'].str.split(',')
    resource_df = resource_df.explode('subject')

    resource_df = resource_df[resource_df['subject'] != '']
    subject_hist = resource_df['subject'].value_counts()

    return list(subject_hist[subject_hist >= 2].keys())


def _fetch_course(course_id):
    return Course.query.filter_by(course_id=course_id)[0]


def _update_form_according_to_resource(form, resource):
    form.display_name.data = resource.display_name
    form.link.data = resource.link
    form.type.data = resource.type
    form.solution.data = resource.solution
    form.recording.data = resource.recording
    form.is_out_of_date.data = resource.is_out_of_date
    form.is_solution_partial.data = resource.is_solution_partial
    form.semester.data = resource.semester
    form.deadline_week.data = resource.deadline_week
    form.subject.data = resource.subject
    return form


def _update_resource_according_to_form(resource, form):
    actual_resource = db.session.query(Resource).filter_by(resource_id=int(resource.resource_id)).first()

    actual_resource.display_name = form.display_name.data
    actual_resource.type = form.type.data
    actual_resource.link = _strip_after_file_extension(form.link.data)
    actual_resource.solution = _strip_after_file_extension(form.solution.data)
    actual_resource.recording = form.recording.data
    actual_resource.is_out_of_date = form.is_out_of_date.data
    actual_resource.is_solution_partial = form.is_solution_partial.data
    actual_resource.deadline_week = form.deadline_week.data
    actual_resource.semester = form.semester.data
    actual_resource.subject = form.subject.data

    db.session.commit()
    db.session.refresh(actual_resource)

    return [(actual_resource.resource_id, actual_resource.display_name, actual_resource.type, actual_resource.semester, actual_resource.comments)]


def _strip_after_file_extension(s):
    for extension in ['.pdf', '.docx', '.pptx']:
        if extension in s:
            return s.split(extension)[0] + extension
    else:
        return s


def _insert_resource_according_to_form(form, course_id):
    updated_resources = []

    num = 1

    if form.type.data in ['exercise_full', 'exam_full']:
        form.type.data = form.type.data[:-5]
        num = int(form.questions_count.data)

    for i in range(num):
        name = form.display_name.data
        if num > 1:
            name += ' שאלה ' + str((i+1))
        resource = Resource(display_name=name,
                            type=form.type.data,
                            link=_strip_after_file_extension(form.link.data),
                            solution=_strip_after_file_extension(form.solution.data),
                            recording=form.recording.data,
                            is_out_of_date=form.is_out_of_date.data,
                            is_solution_partial=form.is_solution_partial.data,
                            deadline_week=form.deadline_week.data,
                            semester=form.semester.data,
                            likes=0,
                            subject=form.subject.data,
                            course_id=course_id)
        db.session.add(resource)
        db.session.commit()
        db.session.refresh(resource)

        updated_resources += [(resource.resource_id, resource.display_name, resource.type, resource.semester, resource.comments)]

    return updated_resources


def _get_subjects(resources_df):
    list_of_lists = [
        resource[1].subject for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _alternative_sort(series):
    if series.dtype == object:
        series[series.str.startswith('אביב 20')] = series[series.str.startswith('אביב 20')] + 'א'
        series[series.str.startswith('קיץ 20')] = series[series.str.startswith('קיץ 20')] + 'ב'

        series[series.str.startswith('אביב 20')] = series[series.str.startswith('אביב 20')].str.replace('אביב', '')
        series[series.str.startswith('קיץ 20')] = series[series.str.startswith('קיץ 20')].str.replace('קיץ', '')
        series[series.str.startswith('חורף 20')] = series[series.str.startswith('חורף 20')].str.replace('חורף', '').str.replace('-', 'ג')

        series[series.str.startswith('לקראת המבחן')] = 'תתת' + series[series.str.startswith('לקראת המבחן')]

        series[series.str.startswith('מבוא להרצאה')] = 'אאאא' + series[series.str.startswith('מבוא להרצאה')]
        series[series.str.startswith('הרצאה')] = 'אאא' + series[series.str.startswith('הרצאה')]
        series[series.str.startswith('מבוא לתרגול')] = 'אא' + series[series.str.startswith('מבוא לתרגול')]
        series[series.str.startswith('תרגול')] = 'א' + series[series.str.startswith('תרגול')]
        for digit in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            series[series.str.endswith(' '+digit)] = series[series.str.endswith(' '+digit)].apply(lambda x: x[:-1] + '0'+digit)
            for addend in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
                series[series.str.endswith(' '+digit+addend)] = series[series.str.endswith(' '+digit+addend)].apply(lambda x: x[:-2] + '0'+digit+addend)
            for t in ['הרצאה', 'תרגול', 'תרגיל בית', 'גיליון', 'שאלה', 'שבוע']:
                series = series.str.replace(t + ' ' + digit + ' ', t+' 0' + digit+' ')
                for addend in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
                    series = series.str.replace(t + ' ' + digit + addend, t+' 0' + digit+addend)

    return series


def _fetch_resources(course_id, tab):
    resource_df = pd.DataFrame([vars(s) for s in pd.Series(Resource.query.filter_by(course_id=course_id).all(), dtype=object)])

    if len(resource_df) == 0:
        return pd.DataFrame()

    if tab == 'semester':
        resource_df = resource_df[(resource_df['type'] == 'lecture')]
        resource_df.sort_values(['deadline_week', 'display_name'], key=_alternative_sort, inplace=True)
        resource_df['deadline_week'] = resource_df['deadline_week'].fillna('המבחן')
        resource_df.insert(0, 'main', resource_df['deadline_week'])

    if tab == 'exercises':
        resource_df = resource_df[resource_df['type'] == 'exercise']
        resource_df.sort_values(['semester', 'display_name'], key=_alternative_sort,  ascending=[False, True], inplace=True)
        resource_df.insert(0, 'main', resource_df['semester'])

    if tab == 'exams':
        resource_df = resource_df[resource_df['type'] == 'exam']
        resource_df.sort_values(['semester', 'display_name'], key=_alternative_sort,  ascending=[False, True], inplace=True)
        resource_df.insert(0, 'main', resource_df['semester'])

    if tab == 'archive':
        resource_df = resource_df[resource_df['type'] == 'other']
        resource_df.insert(0, 'main', resource_df['semester'])
        resource_df.sort_values(['likes', 'display_name'], key=_alternative_sort, ascending=[False, True], inplace=True)

    resources_extended_df = resource_df
    if current_user.is_authenticated:
        resource_to_user = pd.DataFrame([vars(s) for s in pd.Series(ResourceToUser.query.filter_by(
            user_id=current_user.user_id).all(), dtype=object)])

        if len(resource_to_user) > 0:
            resource_to_user.drop('id', axis=1, inplace=True)
            resource_to_user.drop('user_id', axis=1, inplace=True)
            resources_extended_df = pd.merge(how='left',
                                             left=resource_df, right=resource_to_user, on="resource_id")

    if 'subject' in resources_extended_df.keys():
        resources_extended_df['subject'] = resources_extended_df['subject'].apply(
            lambda x: x.split(',') if x else "")

    resources_extended_df = resources_extended_df.fillna(0)
    return resources_extended_df


def _update_resource_discord_link(resource_id, discord_link):
    Resource.query.filter_by(resource_id=resource_id).update({'comments': discord_link})
    db.session.commit()
