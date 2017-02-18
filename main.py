#!/usr/bin/env python3

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

import config

class LoginForm(FlaskForm):
    email = StringField(validators=[Required()])
    password = PasswordField(validators=[Required()])
    submit = SubmitField()

app = Flask(__name__)
app.config.from_object(config)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

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
    return str(article.id)+'++'+str(article.title)+'++'+str(article.text)

@app.route('/')
def index():
    return render_template('index.html', text='Hello, My Site!')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


