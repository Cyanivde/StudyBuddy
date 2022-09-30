from flask import render_template, request, abort
from flask_login import current_user
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


@ app.route('/createresource/<course_id>', methods=['GET', 'POST'])
def createresource(course_id):
    return _update_resource(course_id=course_id, is_existing_resource=False)


@app.route('/editresource/<course_id>', methods=['GET', 'POST'])
def editresource(course_id):
    return _update_resource(course_id=course_id, is_existing_resource=True, resource_id=request.args.get('resource_id'))


@ app.route('/updateresourcetouser', methods=['POST'])
def update_resource_to_user():
    return _update_resource_to_user()


@app.route('/course/<course_id>', methods=['GET', 'POST'])
def course(course_id):
    return _course(course_id, "semester")


@app.route('/exams/<course_id>', methods=['GET', 'POST'])
def exams(course_id):
    return _course(course_id, "exams")


@app.route('/archive/<course_id>', methods=['GET', 'POST'])
def archive(course_id):
    return _course(course_id, "archive")
