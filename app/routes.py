from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, SubjectsForm, UploadForm, CreateCourseForm, CourseResourcesForm, SearchForm
from app.models import ResourceToCourse, ResourceToUser, User, Subject, Resource, Course
import pandas as pd
import json

admins = ['yaniv', 'gilad', 'hili.levy', 'admin']


@app.route('/')
def index():
    courses = Course.query.all()
    return render_template("index.html", title='Home Page', courses=courses, admins=admins)


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    all_subjects = Subject.query.all()
    all_subject_names = [subject.name.strip() for subject in all_subjects]
    if (all_subject_names is not None):
        all_subject_names.sort()

    form = SubjectsForm()
    if form.validate_on_submit():
        all_subject_names = form.subjects.data.split("\n")
        if (all_subject_names is not None):
            all_subject_names.sort()
        db.session.query(Subject).delete()
        for subject_name in all_subject_names:
            subject = Subject(name=subject_name.strip())
            db.session.add(subject)
        db.session.commit()
        form.subjects.data = "\n".join(all_subject_names)
        return render_template("subjects.html", title='Home Page', form=form, admins=admins)
    form.subjects.data = "\n".join(all_subject_names)
    return render_template("subjects.html", title='Home Page', form=form, admins=admins)


@app.route('/upload/<course_id>', methods=['GET', 'POST'])
def upload(course_id):
    all_subjects = Subject.query.all()
    all_subject_names = [subject.name for subject in all_subjects]
    if (all_subject_names is not None):
        all_subject_names.sort()

    form = UploadForm()
    form.subject.choices = all_subject_names

    if form.validate_on_submit():
        if ('/' not in form.description.data):
            form.description.data = "ללא קטגוריה/"+form.description.data

        resource = Resource(link=form.link.data,
                            specification=form.specification.data,
                            subject=json.dumps(form.subject.data),
                            textdump=form.textdump.data.lower())
        db.session.add(resource)

        db.session.commit()
        db.session.refresh(resource)

        resource_to_course = ResourceToCourse(
            course_id=course_id, resource_id=resource.id, description=form.description.data, importance=0)
        db.session.add(resource_to_course)
        db.session.commit()

        return redirect(url_for('course', course_id=course_id))

    return render_template('upload.html', title='upload', form=form, options=all_subject_names, admins=admins, with_name=True)


@app.route('/edit/<resource_id>', methods=['GET', 'POST'])
def edit(resource_id):
    all_subjects = Subject.query.all()
    all_subject_names = [subject.name for subject in all_subjects]
    if (all_subject_names is not None):
        all_subject_names.sort()

    form = UploadForm()
    form.subject.choices = all_subject_names

    resource = Resource.query.filter_by(id=resource_id).first()

    if form.validate_on_submit():
        resource.link = form.link.data
        resource.specification = form.specification.data
        resource.subject = json.dumps(form.subject.data)
        resource.textdump = form.textdump.data.lower()
        db.session.commit()
        db.session.refresh(resource)
        return redirect(url_for('course', course_id=request.args.get('course_id')))

    else:
        form.link.data = resource.link
        form.specification.data = resource.specification
        form.subject.data = json.loads(resource.subject)
        form.textdump.data = resource.textdump

    return render_template('upload.html', title='upload', form=form, options=all_subject_names, admins=admins, with_name=False)


@app.route('/createcourse', methods=['GET', 'POST'])
def createcourse():
    form = CreateCourseForm()

    if form.validate_on_submit():
        course = Course(name=form.name.data)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('createcourse.html', title='createcourse', form=form, admins=admins)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('שם המשתמש או הסיסמה שגויים')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, admins=admins)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.lower(),
                    email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', title='register', form=form, admins=admins)


@app.route('/course/<course_id>', methods=['GET', 'POST'])
def course(course_id):
    course = Course.query.filter_by(id=course_id).first_or_404()

    resources_df = _fetch_resources(course_id)

    if 'subject' not in resources_df.keys():
        return render_template('course.html', subjects=[], filtered_subject=[], course=course, current_search=request.form.get('query'), resources=dict(), admins=admins)

    all_subjects = _get_subjects(resources_df)

    resources_df = _filter_resources(resources_df, query=request.form.get(
        'query'), subject=request.form.getlist('subject'))

    if request.method == "POST":
        if current_user.is_authenticated:
            resources_df = _fetch_resources(course_id)

            all_subjects = _get_subjects(resources_df)

            resources_df = _filter_resources(resources_df, query=request.form.get(
                'query'), subject=request.form.getlist('subject'))

    multi_resources = dict()
    if len(resources_df) > 0:
        resources_df[['directory', 'description']
                     ] = resources_df['description'].str.split('/', 1, expand=True)

        for directory in resources_df['directory']:
            multi_resources[directory] = resources_df[resources_df['directory'] == directory]

    return render_template('course.html', subjects=all_subjects, filtered_subjects=request.form.getlist('subject'), course=course, current_search=request.form.get('query'), resources=multi_resources, admins=admins)


@app.route('/updatecourse/<course_id>', methods=['GET', 'POST'])
def updatecourse(course_id):
    course = Course.query.filter_by(id=course_id).first_or_404()

    form = CourseResourcesForm()
    resources_df = _fetch_resources(course_id)
    if not form.validate_on_submit():
        form.resources.data = _resources_to_textarea(resources_df)
        return render_template('updatecourse.html', form=form, course=course, admins=admins)

    else:
        resources = [(line.split(' | ')[0], line.split(' | ')[1])
                     for line in form.resources.data.split('\n') if ' ' in line]
        db.session.query(ResourceToCourse).filter_by(
            course_id=course_id).delete()
        for resource in resources:
            resource_to_course = ResourceToCourse(
                course_id=course_id, resource_id=resource[0], description=resource[1], importance=0)
            db.session.add(resource_to_course)
        db.session.commit()

        return render_template('updatecourse.html', form=form, course=course, admins=admins)


def _fetch_resources(course_id):
    resource_to_course_df = pd.read_sql(ResourceToCourse.query.filter_by(
        course_id=course_id).statement, db.session.bind)

    resource_ids = set(resource_to_course_df['resource_id'])

    resources_df = pd.read_sql(Resource.query.filter(
        Resource.id.in_(resource_ids)).statement, db.session.bind)

    resources_extended_df = resource_to_course_df
    if len(resources_df) > 0:
        resources_extended_df = pd.merge(how='right',
                                         left=resources_df, right=resource_to_course_df, left_on="id", right_on="resource_id", suffixes=['_a', ''])

    if current_user.is_authenticated:
        resource_to_user = pd.read_sql(ResourceToUser.query.filter_by(
            user_id=current_user.id).statement, db.session.bind)

        if len(resource_to_user) > 0:
            resources_extended_df = pd.merge(how='left',
                                             left=resources_extended_df, right=resource_to_user, left_on="resource_id", right_on="resource_id", suffixes=['', '_u'])

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


def _resources_to_textarea(df):
    return "\n".join(["{0} | {1}".format(
        resource[1].resource_id, resource[1].description) for resource in df.iterrows()])


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

    return resources_extended_df


@ app.route('/updateresource', methods=['POST'])
def updateresource():

    resource_id = request.get_json()['resource_id']
    val = request.get_json()['val']

    if current_user.is_authenticated:
        db.session.query(ResourceToUser).filter_by(
            user_id=current_user.id, resource_id=resource_id).delete()

        resource_to_user = ResourceToUser(
            user_id=current_user.id, resource_id=resource_id, done=val)
        db.session.add(resource_to_user)
        db.session.commit()

    return render_template("index.html", title='Home Page', admins=admins)


@ app.route('/resource/<resource_id>', methods=['GET', 'POST'])
def resource(resource_id):
    resource = Resource.query.filter_by(id=resource_id).first_or_404()

    resource_tuples = []

    resource_descriptions = ResourceToCourse.query.filter_by(
        resource_id=resource_id).all()

    for res in resource_descriptions:
        course = Course.query.filter_by(id=res.course_id).first()
        resource_tuples += [(res.description.split('/')
                             [1], course.name, res.course_id)]

    return render_template('resource.html', resource=resource, resource_tuples=resource_tuples, admins=admins)


@ app.route('/delete/<resource_id>')
def delete(resource_id):
    results = db.session.query(ResourceToCourse).filter_by(
        resource_id=resource_id)
    message = "Cannot delete resource, it is linked in courses: "
    courses_list = []
    for result in results:
        courses_list += [result.course_id]

    if (len(courses_list) > 0):
        return render_template('delete.html', message=message + str(courses_list), admins=admins)

    db.session.query(Resource).filter_by(
        id=resource_id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@ app.route('/deletecourse/<course_id>')
def deletecourse(course_id):
    if current_user.is_authenticated and current_user.username in admins:
        db.session.query(ResourceToCourse).filter_by(
            course_id=course_id).delete()
        db.session.query(Course).filter_by(
            id=course_id).delete()
        db.session.commit()
    return redirect(url_for('index'))


class Object(object):
    pass
