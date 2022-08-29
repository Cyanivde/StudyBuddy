from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func
import hashlib


from app import app, db
from app.forms import LoginForm, RegistrationForm, UpdateResourceForm, CourseResourcesForm
from app.models import ResourceToCourse, ResourceToUser, User, Subject, Resource, Course
import pandas as pd
import json


@app.route('/')
def index():
    return render_template("index.html", courses=Course.query.all())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('register.html', form=form)

    # Form was submitted with valid input
    else:
        user = User(username=form.username.data.lower(), email=form.email.data.lower(), is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    # Form was not yet submitted, or form was submitted with invalid input
    if not form.validate_on_submit():
        return render_template('login.html', title='Sign In', form=form)

    # Form was submitted with valid input
    else:
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('שם המשתמש או הסיסמה שגויים')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/resource/<resource_id>', methods=['GET', 'POST'])
def resource(resource_id):
    resource_df = _fetch_resource_df(resource_id)
    resource = resource_df.iloc[0]
    resource_titles_df = resource_df[['course_id', 'course_name', 'rname', 'rname_part']]
    return render_template('resource.html', resource, resource_titles_df)


@ app.route('/createresource/<course_id>', methods=['GET', 'POST'])
def createresource(course_id):
    return _update_resource(course_id=course_id, is_existing_resource=False)


@app.route('/editresource/<course_id>', methods=['GET', 'POST'])
def editresource(course_id):
    return _update_resource(course_id=course_id, is_existing_resource=True, resource_id=request.args.get('resource_id'))


@app.route('/exams/<course_id>', methods=['GET', 'POST'])
def exams(course_id):
    return _course(course_id, "exams")


@app.route('/archive/<course_id>', methods=['GET', 'POST'])
def archive(course_id):
    return _course(course_id, "archive")


@app.route('/course/<course_id>', methods=['GET', 'POST'])
def course(course_id):
    return _course(course_id, "semester")


def _update_resource(course_id, is_existing_resource, resource_id=None):
    form = UpdateResourceForm()

    subject_list = _fetch_subject_list()
    form.subject.choices = subject_list

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


def _course(course_id, tab):
    course = Course.query.filter_by(course_id=course_id).first_or_404()

    resources_df = _fetch_resources(course_id, tab)
    if len(resources_df) == 0:
        return render_template('course.html', subjects=[], filtered_subject=[], course=course, current_search=request.form.get('query'), resources=dict())

    resources_df = _add_fake_rows(resources_df)
    all_subjects = _get_subjects(resources_df)

    resources_df = _filter_resources(resources_df, query=request.form.get(
        'query'), subject=request.form.getlist('subject'))

    if request.method == "POST":
        if current_user.is_authenticated:
            resources_df = _fetch_resources(course_id, tab)
            resources_df = _add_fake_rows(resources_df)
            all_subjects = _get_subjects(resources_df)

            resources_df = _filter_resources(resources_df, query=request.form.get(
                'query'), subject=request.form.getlist('subject'))

    multi_resources = dict()
    if len(resources_df) > 0:
        for header in resources_df['header']:
            multi_resources[header] = resources_df[resources_df['header'] == header]

    return render_template('course.html', subjects=all_subjects, filtered_subjects=request.form.getlist('subject'), course=course, current_search=request.form.get('query'), resources=multi_resources, tab=tab)


@app.route('/updatecourse/<course_id>', methods=['GET', 'POST'])
def updatecourse(course_id):
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

        db.session.query(ResourceToCourse).filter_by(
            course_id=course_id).delete()

        order_in_tab = 1
        for resource in resources:
            resource_to_course = ResourceToCourse(
                course_id=course_id, resource_id=resource[0], header=resource[1], rname=resource[2], rname_part=resource[3], tab="semester", order_in_tab=order_in_tab)
            db.session.add(resource_to_course)
            order_in_tab += 1

        order_in_tab = 1
        for resource in archive:
            resource_to_course = ResourceToCourse(
                course_id=course_id, resource_id=resource[0], header=resource[1], rname=resource[2], rname_part=resource[3], tab="archive", order_in_tab=order_in_tab)
            db.session.add(resource_to_course)
            order_in_tab += 1

        order_in_tab = 1
        for resource in exams:
            resource_to_course = ResourceToCourse(
                course_id=course_id, resource_id=resource[0], header=resource[1], rname=resource[2], rname_part=resource[3], tab="exams", order_in_tab=order_in_tab)
            db.session.add(resource_to_course)
            order_in_tab += 1

        db.session.commit()

        return render_template('updatecourse.html', form=form, course=course)


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
            folded_row['textdump'] = ' '.join(resources_extended_df[resources_extended_df['rname']
                                                                    == folded_row_name]['textdump'])
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


def _get_subjects(resources_df):
    list_of_lists = [
        resource[1].subject for resource in resources_df.iterrows()]
    return set([x for xs in list_of_lists for x in xs])


def _filter_resources(resources_extended_df, query, subject):
    if query and subject:
        resources_extended_df['show'] = (resources_extended_df['textdump'].str.contains(query.lower())) & (
            resources_extended_df['subject'].apply(lambda x: any([subj in x for subj in subject])))
    elif query:
        resources_extended_df['show'] = resources_extended_df['textdump'].str.contains(
            query.lower())
    elif subject:
        resources_extended_df['show'] = resources_extended_df['subject'].apply(
            lambda x: any([subj in x for subj in subject]))
    else:
        resources_extended_df['show'] = True

    if (query):
        resources_extended_df['occurrences'] = resources_extended_df['textdump'].str.count(
            query.lower())

    resources_extended_df = resources_extended_df[resources_extended_df['show']]

    return resources_extended_df


@ app.route('/updateresource', methods=['POST'])
def updateresource():
    resource_id = request.get_json()['resource_id']
    val = request.get_json()['val']

    if current_user.is_authenticated:
        db.session.query(ResourceToUser).filter_by(
            user_id=current_user.user_id, resource_id=resource_id).delete()

        resource_to_user = ResourceToUser(
            user_id=current_user.user_id, resource_id=resource_id, done=val)
        db.session.add(resource_to_user)
        db.session.commit()

    return render_template("index.html", title='Home Page')


class Object(object):
    pass


###### END ######

def _fetch_subject_list():
    subject_names = [subject.subject_name for subject in Subject.query.all()]
    if subject_names is not None:
        subject_names.sort()

    return subject_names


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


def _update_form_according_to_resource(form, resource):
    form.link.data = resource.link
    form.solution.data = resource.solution
    form.recording.data = resource.recording
    form.subject.data = json.loads(resource.subject)
    form.textdump.data = resource.textdump
    return form


def _update_resource_according_to_form(resource, form):
    actual_resource = db.session.query(Resource).filter_by(resource_id=int(resource.resource_id)).first()

    actual_resource.link = form.link.data
    actual_resource.solution = form.solution.data
    actual_resource.recording = form.recording.data
    actual_resource.subject = json.dumps(form.subject.data)
    actual_resource.textdump = form.textdump.data.lower()

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
                        subject=json.dumps(form.subject.data),
                        textdump=form.textdump.data.lower())
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
