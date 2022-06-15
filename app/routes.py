from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import all_
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, SubjectsForm
from app.models import User, Subject


@app.route('/')
def index():
    return render_template("index.html", title='Home Page')


@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    all_subjects = Subject.query.all()

    all_subject_names = [subject.name for subject in all_subjects]

    form = SubjectsForm()
    if form.validate_on_submit():
        all_subject_names = form.subjects.data.split("\n")

        db.session.query(Subject).delete()
        for subject_name in all_subject_names:
            subject = Subject(name=subject_name)
            db.session.add(subject)
        db.session.commit()
        form.subjects.data = "\n".join(all_subject_names)
        return render_template("subjects.html", title='Home Page', form=form)
    form.subjects.data = "\n".join(all_subject_names)
    return render_template("subjects.html", title='Home Page', form=form)


@app.route('/upload')
def upload():
    return render_template("index.html", title='Home Page')


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
