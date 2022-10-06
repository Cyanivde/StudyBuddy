from flask import render_template
from app import app
from app.models import Course
from app.register import _register
from app.login import _login
from app.logout import _logout
from app.resource import _resource
from app.update_resource import _update_resource
from app.update_resource_to_user import _update_resource_to_user
from app.course import _course


@app.route('/')
def index():
    return render_template("index.html", courses=Course.query.all())


@app.route('/register', methods=['GET', 'POST'])
def register():
    return _register()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return _login()


@app.route('/logout')
def logout():
    return _logout()


@app.route('/resource/<resource_id>', methods=['GET', 'POST'])
def resource(resource_id):
    return _resource(resource_id)


@ app.route('/<institute>/<institute_course_id>/createresource', methods=['GET', 'POST'])
def createresource(institute, institute_course_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _update_resource(course_id=str(course_df.course_id), institute=institute, institute_course_id=institute_course_id, is_existing_resource=False)


@app.route('/<institute>/<institute_course_id>/editresource/<resource_id>', methods=['GET', 'POST'])
def editresource(institute, institute_course_id, resource_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _update_resource(course_id=str(course_df.course_id), institute=institute, institute_course_id=institute_course_id, is_existing_resource=True, resource_id=resource_id)


@ app.route('/updateresourcetouser', methods=['POST'])
def update_resource_to_user():
    return _update_resource_to_user()


@app.route('/<institute>/<institute_course_id>', methods=['GET', 'POST'])
def course(institute, institute_course_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _course(str(course_df.course_id), "semester")


@app.route('/<institute>/<institute_course_id>/exercises', methods=['GET', 'POST'])
def exercises(institute, institute_course_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _course(str(course_df.course_id), "exercises")


@app.route('/<institute>/<institute_course_id>/exams', methods=['GET', 'POST'])
def exams(institute, institute_course_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _course(str(course_df.course_id), "exams")


@app.route('/<institute>/<institute_course_id>/archive', methods=['GET', 'POST'])
def archive(institute, institute_course_id):
    course_df = Course.query.filter_by(course_institute_english=institute, course_institute_id=institute_course_id).first_or_404()
    return _course(str(course_df.course_id), "archive")
