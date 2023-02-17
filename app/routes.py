from flask import redirect, url_for
from app import app
from app.index import _index
from app.register import _register
from app.login import _login
from app.forgotpassword import _forgotpassword
from app.resetpassword import _resetpassword
from app.logout import _logout
from app.update_resource import _update_resource
from app.update_resource_to_user import _update_resource_to_user
from app.course import _course


@app.route('/')
def index():
    return _index()


@app.route('/register', methods=['GET', 'POST'])
def register():
    return _register()


@app.route('/login', methods=['GET', 'POST'])
def login():
    return _login()


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    return _forgotpassword()


@app.route('/resetpassword/<token>', methods=['GET', 'POST'])
def resetpassword(token):
    return _resetpassword(token)


@app.route('/logout')
def logout():
    return _logout()


@app.route('/<course_institute>/<course_institute_id>/create_resource', methods=['GET', 'POST'])
def create_resource(course_institute, course_institute_id):
    return _update_resource(course_institute, course_institute_id, is_existing_resource=False)


@app.route('/<course_institute>/<course_institute_id>/edit_resource/<resource_id>', methods=['GET', 'POST'])
def edit_resource(course_institute, course_institute_id, resource_id=None):
    return _update_resource(course_institute, course_institute_id, is_existing_resource=True, resource_id=resource_id)


@ app.route('/updateresourcetouser', methods=['POST'])
def update_resource_to_user():
    return _update_resource_to_user()


@app.route('/<course_institute>/<course_institute_id>/<tab>', methods=['GET', 'POST'])
def course(course_institute, course_institute_id, tab):
    return _course(course_institute, course_institute_id, tab)


@app.route('/<course_institute>/<course_institute_id>', methods=['GET', 'POST'])
def course_backwards_compatibility(course_institute, course_institute_id):
    return redirect(url_for("course", course_institute=course_institute, course_institute_id=course_institute_id, tab="lessons"))
