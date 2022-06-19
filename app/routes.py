from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import all_
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, SubjectsForm, UploadForm, CreateCourseForm, CourseResourcesForm
from app.models import ResourceToCourse, User, Subject, Resource, Course


@app.route('/')
def index():
    courses = Course.query.all()
    return render_template("index.html", title='Home Page', courses=courses)


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    all_subjects = Subject.query.all()
    all_subject_names = [subject.name for subject in all_subjects]
    if (all_subject_names is not None):
        all_subject_names.sort()

    form = SubjectsForm()
    if form.validate_on_submit():
        all_subject_names = form.subjects.data.split("\n")
        if (all_subject_names is not None):
            all_subject_names.sort()
        db.session.query(Subject).delete()
        for subject_name in all_subject_names:
            subject = Subject(name=subject_name)
            db.session.add(subject)
        db.session.commit()
        form.subjects.data = "\n".join(all_subject_names)
        return render_template("subjects.html", title='Home Page', form=form)
    form.subjects.data = "\n".join(all_subject_names)
    return render_template("subjects.html", title='Home Page', form=form)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    all_subjects = Subject.query.all()
    all_subject_names = [subject.name for subject in all_subjects]
    if (all_subject_names is not None):
        all_subject_names.sort()

    form = UploadForm()
    form.subject.choices = all_subject_names

    if form.validate_on_submit():
        resource = Resource(link=form.link.data,
                            specification=form.specification.data,
                            subject=form.subject.data,
                            textdump=form.textdump.data.lower())
        db.session.add(resource)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('upload.html', title='upload', form=form)


@app.route('/createcourse', methods=['GET', 'POST'])
def createcourse():
    form = CreateCourseForm()

    if form.validate_on_submit():
        course = Course(name=form.name.data)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('createcourse.html', title='createcourse', form=form)


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
    return render_template('login.html', title='Sign In', form=form)


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
    return render_template('register.html', title='register', form=form)


@app.route('/course/<course_id>', methods=['GET', 'POST'])
def course(course_id):
    course = Course.query.filter_by(id=course_id).first_or_404()

    resources = ResourceToCourse.query.filter_by(course_id=course_id)

    form = CourseResourcesForm()
    if form.validate_on_submit():
        resources = [(line.split(']')[0][-1], ' '.join(line.split(' ')[1:-1])[:-1],
                      line.split(': ')[-1]) for line in form.resources.data.split('\n') if ' ' in line]

        db.session.query(ResourceToCourse).filter_by(
            course_id=course_id).delete()
        for resource in resources:
            resource_to_course = ResourceToCourse(
                course_id=course_id, resource_id=resource[2], description=resource[1], importance=resource[0])
            db.session.add(resource_to_course)
        db.session.commit()
        return render_template('course.html', form=form, course=course, existing_resources=resources)
    form.resources.data = "\n".join(["[{0}] {1}: {2}".format(
        resource.importance, resource.description, resource.resource_id) for resource in resources])
    return render_template('course.html', form=form, course=course, existing_resources=resources)


@app.route('/resource/<resource_id>', methods=['GET'])
def resource(resource_id):
    resource = Resource.query.filter_by(id=resource_id).first_or_404()

    return render_template('resource.html', resource=resource)


@app.route('/search', methods=['POST'])
def searchredirection():
    return redirect(url_for('search', query=request.form.get("searchbox", "")))


@app.route('/delete/<resource_id>')
def delete(resource_id):
    results = db.session.query(ResourceToCourse).filter_by(
        resource_id=resource_id)
    message = "Cannot delete resource, it is linked in courses: "
    courses_list = []
    for result in results:
        courses_list += [result.course_id]

    if (len(courses_list) > 0):
        return render_template('delete.html', message=message + str(courses_list))

    db.session.query(Resource).filter_by(
        id=resource_id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/search/<query>', methods=['GET'])
def search(query):
    resources = Resource.query.filter(
        Resource.textdump.contains(query.lower())).all()

    resource_to_occurences = dict()
    resource_to_descriptions = dict()
    resource_to_link = dict()

    for resource in resources:
        resource_to_occurences[resource.id] = resource.textdump.count(
            query.lower())
        resource_to_link[resource.id] = resource.link

    resource_to_course = ResourceToCourse.query.filter(
        ResourceToCourse.resource_id.in_(resource_to_occurences.keys()))

    resource_ids_in_course = {
        result_resource.resource_id: result_resource.description for result_resource in resource_to_course}

    for resource_id in resource_to_occurences.keys():
        if resource_id in resource_ids_in_course:
            resource_to_descriptions[resource_id] = resource_ids_in_course[resource_id]
        else:
            resource_to_descriptions[resource_id] = resource_to_link[resource_id]

    result_resources_final = []
    for resource_id in resource_to_occurences.keys():
        resource = Object()
        resource.resource_id = resource_id
        resource.description = resource_to_descriptions[resource_id]
        resource.occurrences = resource_to_occurences[resource_id]
        result_resources_final += [resource]

    result_resources_final.sort(key=lambda x: x.occurrences, reverse=True)

    return render_template('search.html', query=query, result_resources=result_resources_final)


class Object(object):
    pass
