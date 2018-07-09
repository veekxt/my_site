#!/usr/bin/env python3
import os
import time

from datetime import datetime
from flask import Flask, request, render_template, url_for, flash, Blueprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from sqlalchemy import desc
from werkzeug.utils import secure_filename, redirect
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_login import LoginManager
import json
from flask_login import current_user, login_required

from my_utils import my_secure_filename
from data_model import db, Article, User, Tag
from auth import login_manager

import config_t
from auth import auth as auth_blueprint

app = Flask(__name__)
app.config.from_object(config_t)
bootstrap = Bootstrap(app)
db.init_app(app)
login_manager.init_app(app)
app.register_blueprint(auth_blueprint)


@app.route("/utils")
def utils():
    return render_template('utils.html')


@app.route('/')
def index():
    page = request.args.get("page", 1, type=int)
    pagination = Article.query.order_by(desc(Article.time)).paginate(page, per_page=app.config['POSTS_PER_PAGE'],
                                                             error_out=True)
    articles=pagination.items

    return render_template('index.html', articles=articles, pagination=pagination)


@app.route('/up', methods=['GET', 'POST'])
def my_upload():
    if request.method == "POST":
        f = request.files['inputfile']
        if os.name == "posix":
            upload_path = os.path.join("/myvps", 'upload', my_secure_filename(f.filename))
        else:
            upload_path = os.path.join("e:\\tmp", '', my_secure_filename(f.filename))

        f.save(upload_path)
        return redirect(url_for('my_upload'))
    return render_template('up.html')


@app.route('/write_article', methods=['GET'])
@login_required
def write_article():
    return render_template('write_article.html')


@app.route('/post_article', methods=['POST'])
@login_required
def post_article():
    if current_user.access != 0:
        # flash("当前用户没有权限发布文章！")
        return "Cant access!"
    try:
        article_info = json.loads(request.get_data())
        article = Article(
            author=current_user.id,
            time=datetime.now(),
            title=article_info["title"],
            text=article_info["main"])
        if len(article_info["title"]) == 0:
            return "Has No Title!"
        db.session.add(article)
        db.session.commit()
    except:
        db.session.rollback()
        return "Unknown error!"
    return "OK"

@app.route('/select_tags')
def select_tags():
    rs = []
    all = Tag.query.all()
    for i in all:
        rs.append(i.name)
    return json.dumps(rs)

@app.route("/article/<id>")
def a_article(id):
    return render_template("article.html",id=id)

@app.route("/article_info/<id>")
def a_article_info(id):
    article = Article.query.get(int(id))
    article_json = {
        "title":article.title,
        "time":str(article.time),
        "text":article.text,
        "author":article.user.name
    }
    return json.dumps(article_json)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)
