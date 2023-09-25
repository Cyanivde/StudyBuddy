
import pandas as pd
from flask_login import current_user

from app import db
from app.models import Resource, ResourceToUser

SEMESTERS_LIST = ['חורף 2023-2024',
                  'קיץ 2023',
                  'אביב 2023',
                  'חורף 2022-2023',
                  'קיץ 2022',
                  'אביב 2022',
                  'חורף 2021-2022',
                  'קיץ 2021',
                  'אביב 2021',
                  'חורף 2020-2021',
                  'קיץ 2020',
                  'אביב 2020',
                  'חורף 2019-2020',
                  'קיץ 2019',
                  'אביב 2019',
                  'חורף 2018-2019',
                  'קיץ 2018',
                  'אביב 2018',
                  'חורף 2017-2018',
                  'קיץ 2017',
                  'אביב 2017',
                  'חורף 2016-2017',
                  'קיץ 2016',
                  'אביב 2016',
                  'חורף 2015-2016',
                  'קיץ 2015',
                  'אביב 2015',
                  'חורף 2014-2015',
                  'קיץ 2014',
                  'אביב 2014',
                  'חורף 2013-2014',
                  'קיץ 2013',
                  'אביב 2013',
                  'חורף 2012-2013',
                  'קיץ 2012',
                  'אביב 2012',
                  'חורף 2011-2012',
                  'קיץ 2011',
                  'אביב 2011',
                  'חורף 2010-2011',
                  'קיץ 2010',
                  'אביב 2010',
                  'חורף 2009-2010',
                  'קיץ 2009',
                  'אביב 2009',
                  'חורף 2008-2009',
                  'קיץ 2008',
                  'אביב 2008',
                  'חורף 2007-2008',
                  'קיץ 2007',
                  'אביב 2007',
                  'חורף 2006-2007',
                  'קיץ 2006',
                  'אביב 2006',
                  'חורף 2005-2006',
                  'קיץ 2005',
                  'אביב 2005',
                  'חורף 2004-2005',
                  'קיץ 2004',
                  'אביב 2004',
                  'חורף 2003-2004',
                  'קיץ 2003',
                  'אביב 2003',
                  'חורף 2002-2003',
                  'קיץ 2002',
                  'אביב 2002',
                  'חורף 2001-2002',
                  'קיץ 2001',
                  'אביב 2001',
                  'חורף 2000-2001',
                  'קיץ 2000',
                  'אביב 2000']


def _fetch_subject_list(course_institute, course_institute_id, resource_df=None):
    if resource_df is None:
        resource_df = _fetch_resources(course_institute=course_institute,
                                       course_institute_id=course_institute_id)

    return _get_prominent_values(resource_df, 'subject')


def _fetch_creator_list(course_institute, course_institute_id, resource_df=None):
    if resource_df is None:
        resource_df = _fetch_resources(course_institute=course_institute,
                                       course_institute_id=course_institute_id,)

    return _get_prominent_values(resource_df, 'creator')


def _get_prominent_values(dataframe, column):
    if len(dataframe) == 0:
        return []

    # precedence
    df_1 = dataframe[dataframe['type'] == 'lesson']
    df_2 = dataframe[dataframe['type'] == 'exam']
    df_3 = dataframe[dataframe['type'] == 'other']
    dataframe = pd.concat([df_1, df_2, df_3])

    dataframe[column] = dataframe[column].str.split(',')
    dataframe = dataframe.explode(column)
    dataframe = dataframe[dataframe[column] != '']

    hist = dataframe[column].value_counts(sort=False)
    return list(hist[hist >= 2].keys())


def _fetch_courses(course_institute=None, course_institute_id=None):
    courses_df = pd.read_csv('courses.csv', dtype={
                             'course_institute_id': object})

    if course_institute:
        courses_df = courses_df[courses_df.course_institute ==
                                course_institute]

    if course_institute_id:
        courses_df = courses_df[courses_df.course_institute_id ==
                                course_institute_id]

    return courses_df


def _update_form_according_to_resource(form, resource):
    form.display_name.data = resource.display_name
    form.folder.data = resource.folder
    form.link.data = resource.link
    form.type.data = resource.type
    form.solution.data = resource.solution
    form.recording[0].data = resource.recording
    form.recording_comment[0].data = resource.recording_comment
    form.is_out_of_date.data = resource.is_out_of_date
    form.is_solution_partial.data = resource.is_solution_partial
    form.is_in_recycle_bin.data = resource.is_in_recycle_bin
    form.semester.data = resource.semester
    form.creator.data = resource.creator
    form.subject.data = resource.subject
    return form


def _default_folder(form):
    if "exam" in form.type.data:
        form.folder.data = 'מועד א\''
    elif form.type.data == "lesson":
        form.folder.data = 'הרצאה 1'
    else:
        form.folder.data = 'ללא תיקייה'
    return form


def _update_resource_according_to_form(resource_series, form):
    if form.folder.data == '':
        form = _default_folder(form)

    form.folder.data = form.folder.data.replace("׳", "'")

    if (form.type.data != "exam_full"
            and form.display_name.data == ''):
        form.display_name.data = 'ללא שם'

    resource = db.session.query(Resource).filter_by(
        resource_id=int(resource_series.resource_id)).first()

    resource.display_name = form.display_name.data
    resource.folder = form.folder.data
    resource.type = form.type.data
    resource.link = _strip_after_file_extension(form.link.data)
    resource.solution = _strip_after_file_extension(form.solution.data)
    resource.recording = form.recording[0].data
    resource.recording_comment = form.recording_comment[0].data
    resource.is_out_of_date = form.is_out_of_date.data
    resource.is_solution_partial = form.is_solution_partial.data
    resource.is_in_recycle_bin = form.is_in_recycle_bin.data
    resource.semester = form.semester.data
    resource.subject = form.subject.data
    resource.creator = form.creator.data

    db.session.commit()
    db.session.refresh(resource)


def _strip_after_file_extension(s):
    for extension in ['.pdf', '.docx', '.doc', '.pptx', '.ppt']:
        if extension in s:
            return s.split(extension)[0] + extension
    else:
        return s


def _insert_resource_according_to_form(form,
                                       course_institute,
                                       course_institute_id):
    num_resources = 1

    if form.folder.data == '':
        form = _default_folder(form)

    form.folder.data = form.folder.data.replace("׳", "'")

    if (form.type.data != "exam_full"
            and form.display_name.data == ''):
        form.display_name.data = 'ללא שם'

    if form.type.data == 'exam_full':
        form.type.data = form.type.data[:-5]
        num_resources = int(form.questions_count.data)

    for i in range(num_resources):
        name = form.display_name.data
        if num_resources > 1:
            name += 'שאלה ' + str((i+1))
        resource = Resource(display_name=name,
                            folder=form.folder.data,
                            type=form.type.data,
                            link=_strip_after_file_extension(form.link.data),
                            solution=_strip_after_file_extension(
                                form.solution.data),
                            recording=form.recording[0].data,
                            recording_comment=form.recording_comment[0].data,
                            is_out_of_date=form.is_out_of_date.data,
                            is_solution_partial=form.is_solution_partial.data,
                            is_in_recycle_bin=form.is_in_recycle_bin.data,
                            semester=form.semester.data,
                            likes=0,
                            subject=form.subject.data,
                            creator=form.creator.data,
                            course_institute=course_institute,
                            course_institute_id=course_institute_id)
        db.session.add(resource)
        db.session.commit()
        db.session.refresh(resource)


def _alternative_sort(series):
    """
    This function is designed as an alternative to alphabetical sorting,
    in which, for example, "חורף 2018" is before "אביב 2019".

    This function does not sort. it just changes the original data,
    so that it would fit the desired order after sorting.
    """
    series = series.fillna('')

    if series.dtype == object:
        series[series.str.startswith(
            'אביב 20')] = series[series.str.startswith('אביב 20')] + 'א'
        series[series.str.startswith(
            'קיץ 20')] = series[series.str.startswith('קיץ 20')] + 'ב'

        series[series.str.startswith('אביב 20')] = series[
            series.str.startswith('אביב 20')].str.replace('אביב', '')
        series[series.str.startswith('קיץ 20')] = series[
            series.str.startswith('קיץ 20')].str.replace('קיץ', '')
        series[series.str.startswith('חורף 20')] = series[
            series.str.startswith('חורף 20')].str.replace(
                'חורף', '').str.replace('-', 'ג')

        series[series.str.startswith('לקראת המבחן')] = 'תתת' +  \
            series[series.str.startswith('לקראת המבחן')]
        series[series.str.startswith('מבוא להרצאה')] = 'אאאא' + \
            series[series.str.startswith('מבוא להרצאה')]
        series[series.str.startswith('הרצאה')] = 'אאא' + \
            series[series.str.startswith('הרצאה')]
        series[series.str.startswith('מבוא לתרגול')] = 'אא' + \
            series[series.str.startswith('מבוא לתרגול')]
        series[series.str.startswith('תרגול')] = 'א' + \
            series[series.str.startswith('תרגול')]

        series = series.str.replace('-', ' - ')

        for digit in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            series[series.str.endswith(' '+digit)] = \
                series[series.str.endswith(' '+digit)].apply(
                    lambda x: x[:-1] + '0'+digit)

            for addend in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
                series[series.str.endswith(' '+digit+addend)] = \
                    series[series.str.endswith(' '+digit+addend)].apply(
                        lambda x: x[:-2] + '0'+digit+addend)

            for t in ['הרצאה', 'תרגול', 'שבוע', 'חלק']:
                series = series.str.replace(
                    t + ' ' + digit + ' ', t+' 0' + digit+' ')

                for addend in ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח']:
                    series = series.str.replace(
                        t + ' ' + digit + addend, t+' 0' + digit+addend)

    return series


def _fetch_resources(course_institute=None,
                     course_institute_id=None,
                     resource_id=None):
    # query resources from database
    query = Resource.query
    if course_institute:
        query = query.filter_by(course_institute=course_institute)
    if course_institute_id:
        query = query.filter_by(course_institute_id=course_institute_id)
    if resource_id:
        query = query.filter_by(resource_id=resource_id)
    resource_df = _query_to_dataframe(query.all())

    return resource_df

def _sort_resources(resource_df):
    if resource_df.empty:
        return resource_df

    # sort resources:
    resource_df.sort_values(['semester', 'folder', 'display_name'],
                            key=_alternative_sort,
                            ascending=[False, True, True],
                            inplace=True)

    return resource_df

def _enrich_resources(resource_df, course_institute_id, tab):
    if resource_df.empty:
        return resource_df

    # sort resources:
    resource_df.sort_values(['semester', 'folder', 'display_name'],
                            key=_alternative_sort,
                            ascending=[False, True, True],
                            inplace=True)
    # enrich resources: user's progress
    if current_user.is_authenticated:
        query = ResourceToUser.query.filter_by(
            user_id=current_user.user_id).all()
        resource_to_user = _query_to_dataframe(query)

        if len(resource_to_user) > 0:
            resource_to_user.drop('id', axis=1, inplace=True)
            resource_to_user.drop('user_id', axis=1, inplace=True)
            resource_df = pd.merge(how='left',
                                   left=resource_df,
                                   right=resource_to_user,
                                   on="resource_id")

    # enrich resources: split subjects and creators into lists
    if 'subject' in resource_df.keys():
        resource_df['subject'] = resource_df['subject'].apply(
            lambda x: x.split(',') if x else "")
    if 'creator' in resource_df.keys():
        resource_df['creator'] = resource_df['creator'].apply(
            lambda x: x.split(',') if x else "")

    # enrich resources: links to tscans
    if tab == 'exams':
        resource_df['scans'] = resource_df.apply(
            lambda resource: "https://tscans.cf/?course="
            + course_institute_id
            + "&search=\""
            + resource.semester
            + "\" "
            + resource.folder.replace("'", "%27"),
            axis=1)

    # enrich resources: fill empty fields
    resource_df = resource_df.fillna(0)

    return resource_df


def strip_whitespace(s):
    if isinstance(s, str):
        s = s.strip()
    return s


def _query_to_dataframe(query):
    return pd.DataFrame([vars(s) for s in pd.Series(query, dtype=object)])
