#!/usr/bin/env python3
import os

from flask import Flask, request, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename, redirect
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

from my_utils import my_secure_filename

import config_t


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password_1 = PasswordField(validators=[DataRequired()])
    password_2 = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


app = Flask(__name__)
app.config.from_object(config_t)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    create_at = db.Column(db.DateTime)
    email = db.Column(db.Text)
    name = db.Column(db.Text)


class Article(db.Model):
    __table_name__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    title = db.Column(db.Text)
    text = db.Column(db.Text)


@app.route('/data_test')
def data_test():
    article = Article(time='1999-01-08 04:05:06', title="test_title", text="test_text")
    db.session.add(article)
    db.session.commit()
    return str(article.id) + '++' + str(article.title) + '++' + str(article.text)


@app.route('/')
def index():
    return render_template('index.html', text='Hello, My Site!')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()
    if form.validate_on_submit():
        pass
    return render_template('register.html', form=form)

@app.route('/up', methods=['GET', 'POST'])
def my_upload():
    if request.method == "POST":
        f = request.files['file']
        upload_path = os.path.join("/myvps", 'upload', my_secure_filename(f.filename))
        f.save(upload_path)
        return redirect(url_for('my_upload'))
    return render_template('up.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
