from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return (self.user_id)


class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(500))


class Resource(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500))
    solution = db.Column(db.String(500))
    recording = db.Column(db.String(500))
    comments = db.Column(db.String(500))
    subject = db.Column(db.Text)
    course_id = db.Column(db.Integer)
    display_name = db.Column(db.String(140))
    semester = db.Column(db.String(30))
    deadline_week = db.Column(db.String(140))
    deadline_date = db.Column(db.DateTime)
    is_official = db.Column(db.Boolean)
    is_out_of_date = db.Column(db.Boolean)
    type = db.Column(db.String(20))
    likes = db.Column(db.Integer)


class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_institute = db.Column(db.String(140))
    course_institute_english = db.Column(db.String(140))
    course_institute_id = db.Column(db.String(140))
    course_name = db.Column(db.String(140))
    maintainer = db.Column(db.String(140))
    maintainer_email = db.Column(db.String(140))
    discord_channel_id = db.Column(db.String(50))


class ResourceToUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    resource_id = db.Column(db.Integer)
    done = db.Column(db.Integer)
    like = db.Column(db.Boolean)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
