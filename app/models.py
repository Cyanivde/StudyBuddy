from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500))


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(500))
    solution = db.Column(db.String(500))
    subject = db.Column(db.Text)
    textdump = db.Column(db.Text)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))


class ResourceToCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    course_id = db.Column(db.Integer)
    resource_id = db.Column(db.Integer)
    description = db.Column(db.String(140))
    importance = db.Column(db.Integer)


class ResourceToUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    resource_id = db.Column(db.Integer)
    done = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
