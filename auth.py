from datetime import datetime

from flask import Flask, request, render_template, url_for, flash, Blueprint
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt
from werkzeug.utils import secure_filename, redirect
from data_model import User, db

auth = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.session_protection = None
login_manager.login_view = "auth.user_login"
login_manager.login_message = "访问这个页面需要登录！"

class LoginForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField()


class RegisterForm(FlaskForm):
    email = StringField()
    user_name = StringField(validators=[DataRequired()])
    password_1 = PasswordField(validators=[DataRequired(), EqualTo("password_2")])
    password_2 = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if (request.method == "POST"):
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()
            if user is not None and check_password_hash(user.password_hash, form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get("next") or url_for("index"))
            flash("登录失败！");
    return render_template('login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()
    if (request.method == "POST"):
        if form.validate_on_submit():
            is_success = True
            try:
                user = User(email=form.email.data,
                            create_at=datetime.now(),
                            name=form.user_name.data,
                            password_hash=generate_password_hash(form.password_1.data))
                db.session.add(user)
                db.session.commit()
            except:
                db.session.rollback()
                is_success = False
                pass
            if is_success:
                flash("注册成功, 现在你可以登录了")
                return redirect(url_for("auth.user_login"))
            else:
                flash("注册失败！可能该用户名已被注册")
        else:
            flash("注册失败！输入不合法")
    return render_template('register.html', form=form)


@auth.route("/quit")
@login_required
def user_quit():
    logout_user()
    return redirect(url_for("index"))
