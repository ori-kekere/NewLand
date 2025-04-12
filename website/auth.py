from flask import Blueprint,render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in! Welcome back!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exists.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('That Email already exists!', category='error')
        elif username_exists:
            flash('That Username already exists!', category='error')
        elif password1 != password2:
            flash('Sorry, Passwords don/t match.', category='error')
        elif len(username) < 2:
            flash('That Username is too small!', category='error')
        elif len(password1) < 6:
            flash('That Password is too small!', category='error')
        elif len(email) < 5:
            flash('Email is invalid!', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account has been made! Welcome to New Lands!')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))