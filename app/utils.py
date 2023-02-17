
from flask_login import current_user
from app import db
from app.models import Resource, ResourceToUser
import pandas as pd


def _fetch_subject_list(course_institute, course_institute_id):
    resource_df = _fetch_resources(course_institute=course_institute, course_institute_id=course_institute_id, should_enrich=False)

    if len(resource_df) == 0:
        return []

    resource_df['subject'] = resource_df['subject'].str.split(',')
    resource_df = resource_df.explode('subject')

    resource_df = resource_df[resource_df['subject'] != '']
    subject_hist = resource_df['subject'].value_counts()

    return list(subject_hist[subject_hist >= 2].keys())


def _fetch_instructor_list(course_institute, course_institute_id):
    resource_df = _fetch_resources(course_institute=course_institute, course_institute_id=course_institute_id, should_enrich=False)

    if len(resource_df) == 0:
        return []

    resource_df['instructor'] = resource_df['instructor'].str.split(',')
    resource_df = resource_df.explode('instructor')

    resource_df = resource_df[resource_df['instructor'] != '']
    instructor_hist = resource_df['instructor'].value_counts()

    return list(instructor_hist[instructor_hist >= 2].keys())


def _fetch_courses(course_institute=None, course_institute_id=None):
    courses_df = pd.read_csv('courses.csv', dtype={'course_institute_id': object})

    if course_institute:
        courses_df = courses_df[courses_df.course_institute == course_institute]

    if course_institute_id:
        courses_df = courses_df[courses_df.course_institute_id == course_institute_id]

    return courses_df


def _update_form_according_to_resource(form, resource):
    form.display_name.data = resource.display_name
    form.grouping.data = resource.grouping
    form.link.data = resource.link
    form.type.data = resource.type
    form.solution.data = resource.solution
    form.recording.data = resource.recording
    form.recording2.data = resource.recording2
    form.recording3.data = resource.recording3
    form.recording4.data = resource.recording4
    form.recording5.data = resource.recording5
    form.recording_comment.data = resource.recording_comment
    form.recording2_comment.data = resource.recording2_comment
    form.recording3_comment.data = resource.recording3_comment
    form.recording4_comment.data = resource.recording4_comment
    form.recording5_comment.data = resource.recording5_comment
    form.is_out_of_date.data = resource.is_out_of_date
    form.is_solution_partial.data = resource.is_solution_partial
    form.semester.data = resource.semester
    #form.deadline_week.data = resource.deadline_week
    form.instructor.data = resource.instructor
    form.subject.data = resource.subject
    return form


def _update_resource_according_to_form(resource, form):

    if form.grouping.data == '':
        form.grouping.data = 'ללא תיקייה'

    if form.type.data not in ("exercise_full", "exam_full") and form.display_name.data == '':
        form.display_name.data = 'ללא שם'

    actual_resource = db.session.query(Resource).filter_by(resource_id=int(resource.resource_id)).first()

    actual_resource.display_name = form.display_name.data
    actual_resource.grouping = form.grouping.data
    actual_resource.type = form.type.data
    actual_resource.link = _strip_after_file_extension(form.link.data)
    actual_resource.solution = _strip_after_file_extension(form.solution.data)
    actual_resource.recording = form.recording.data
    actual_resource.recording2 = form.recording2.data
    actual_resource.recording3 = form.recording3.data
    actual_resource.recording4 = form.recording4.data
    actual_resource.recording5 = form.recording5.data
    actual_resource.recording_comment = form.recording_comment.data
    actual_resource.recording2_comment = form.recording2_comment.data
    actual_resource.recording3_comment = form.recording3_comment.data
    actual_resource.recording4_comment = form.recording4_comment.data
    actual_resource.recording5_comment = form.recording5_comment.data
    actual_resource.is_out_of_date = form.is_out_of_date.data
    actual_resource.is_solution_partial = form.is_solution_partial.data
    #actual_resource.deadline_week = form.deadline_week.data
    actual_resource.semester = form.semester.data
    actual_resource.subject = form.subject.data
    actual_resource.instructor = form.instructor.data

    db.session.commit()
    db.session.refresh(actual_resource)

    return [(actual_resource.resource_id, actual_resource.display_name, actual_resource.type, actual_resource.semester, actual_resource.comments)]


def _strip_after_file_extension(s):
    for extension in ['.pdf', '.docx', '.pptx']:
        if extension in s:
            return s.split(extension)[0] + extension
    else:
        return s


def _insert_resource_according_to_form(form, course_institute, course_institute_id):
    updated_resources = []

    num = 1

    if form.grouping.data == '':
        form.grouping.data = 'ללא תיקייה'

    if form.type.data not in ("exercise_full", "exam_full") and form.display_name.data == '':
        form.display_name.data = 'ללא שם'

    if form.type.data in ('exam_full', 'exercise_full'):
        form.type.data = form.type.data[:-5]
        num = int(form.questions_count.data)

    for i in range(num):
        name = form.display_name.data
        if num > 1:
            name += ' שאלה ' + str((i+1))
        resource = Resource(display_name=name,
                            grouping=form.grouping.data,
                            type=form.type.data,
                            link=_strip_after_file_extension(form.link.data),
                            solution=_strip_after_file_extension(form.solution.data),
                            recording=form.recording.data,
                            recording2=form.recording2.data,
                            recording3=form.recording3.data,
                            recording4=form.recording4.data,
                            recording5=form.recording5.data,
                            recording_comment=form.recording_comment.data,
                            recording2_comment=form.recording2_comment.data,
                            recording3_comment=form.recording3_comment.data,
                            recording4_comment=form.recording4_comment.data,
                            recording5_comment=form.recording5_comment.data,
                            is_out_of_date=form.is_out_of_date.data,
                            is_solution_partial=form.is_solution_partial.data,
                            # deadline_week=form.deadline_week.data,
                            semester=form.semester.data,
                            likes=0,
                            num_comments=0,
                            subject=form.subject.data,
                            instructor=form.instructor.data,
                            course_institute=course_institute,
                            course_institute_id=course_institute_id)
        db.session.add(resource)
        db.session.commit()
        db.session.refresh(resource)

        updated_resources += [(resource.resource_id, resource.display_name, resource.type, resource.semester, resource.comments)]

    return updated_resources


def _get_subjects(resources_df):
    list_of_lists = [
        resource[1].subject for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _get_instuctors(resources_df):
    list_of_lists = [
        resource[1].instructor for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _alternative_sort(series):
    series = series.fillna('')

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
            for t in ['הרצאה', 'תרגול', 'תרגיל בית', 'גיליון', 'שאלה', 'שבוע', 'חלק']:
                series = series.str.replace(t + ' ' + digit + ' ', t+' 0' + digit+' ')
                for addend in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
                    series = series.str.replace(t + ' ' + digit + addend, t+' 0' + digit+addend)

    return series


def _fetch_resources(course_institute=None, course_institute_id=None, tab=None, resource_id=None, should_enrich=True):
    # query resources from database
    query = Resource.query
    if course_institute:
        query = query.filter_by(course_institute=course_institute)
    if course_institute_id:
        query = query.filter_by(course_institute_id=course_institute_id)
    if tab:
        if tab == 'lessons':
            query = query.filter_by(type='lecture')
        else:
            query = query.filter_by(type=tab[:-1])
    if resource_id:
        query = query.filter_by(resource_id=resource_id)
    resource_df = _query_to_dataframe(query.all())

    if resource_df.empty:
        return resource_df

    if not should_enrich:
        return resource_df

    resource_df.sort_values(['semester', 'grouping', 'display_name'], key=_alternative_sort,  ascending=[False, True, True], inplace=True)

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

    if 'instructor' in resources_extended_df.keys():
        resources_extended_df['instructor'] = resources_extended_df['instructor'].apply(
            lambda x: x.split(',') if x else "")

    if tab == 'exams':
        if (len(resources_extended_df) > 0):
            resources_extended_df['scans'] = resources_extended_df.apply(lambda x: "https://tscans.cf/?course=" + course_institute_id + "&search=\"" +
                                                                         x.semester + "\" " + x.grouping.replace("'", "%27"), axis=1)

    resources_extended_df = resources_extended_df.fillna(0)

    return resources_extended_df


def _query_to_dataframe(query):
    return pd.DataFrame([vars(s) for s in pd.Series(query, dtype=object)])
