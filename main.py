#!/usr/bin/env python3
import os

from flask import Flask, request, render_template, url_for, flash, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename, redirect
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_login import LoginManager


from my_utils import my_secure_filename
from data_model import db, Article, User
from auth import login_manager

import config_t
from auth import auth as auth_blueprint

app = Flask(__name__)
app.config.from_object(config_t)
bootstrap = Bootstrap(app)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)


@app.route('/data_test')
def data_test():
    article = Article(time='1999-01-08 04:05:06', title="test_title", text="test_text")
    db.session.add(article)
    db.session.commit()
    user = User()
    return str(article.id) + '++' + str(article.title) + '++' + str(article.text)


@app.route("/utils")
def utils():
    #    msg=Message("Wow",sender="XieTAO",recipients=["wlzhizhen@163.com"])
    #    msg.html="<h3>Hello</h3> body"
    #
    #    Mail(app).send(msg)
    return render_template('utils.html')


@app.route('/')
def index():
    return render_template('index.html', text='Hello, My Site!')




@app.route('/up', methods=['GET', 'POST'])
def my_upload():
    if request.method == "POST":
        f = request.files['inputfile']
        if os.name == "posix":
            upload_path = os.path.join("/myvps", 'upload', my_secure_filename(f.filename))
        elif os.name == "nt":
            upload_path = os.path.join("e:\\tmp", '', my_secure_filename(f.filename))
        else:
            pass

        f.save(upload_path)
        return redirect(url_for('my_upload'))
    return render_template('up.html')


if __name__ == '__main__':

    app.run(host="127.0.0.1",port=8000,debug=True)
    from data_model import User
    db.create_all()
