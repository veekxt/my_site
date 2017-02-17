#!/usr/bin/env python3

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required

import config

class LoginForm(FlaskForm):
    email = StringField(validators=[Required()])
    password = PasswordField(validators=[Required()])
    submit = SubmitField()

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config.from_object(config)

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


