from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, db

auth = Blueprint('auth', __name__, template_folder="templates")

#region SignUp
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        data = request.form
        if User.query.filter_by(email=data.get('email')).first():
            flash('Email already registered!', category='error')
        else:
            if handle_sign_up(data):
                return redirect(url_for('views.home'))
    return render_template('sign_up.html', user=current_user)

def handle_sign_up(data):
    # keys = email, firstName, password1, password2
    email = data.get('email', 0)
    name = data.get('firstName', 0)
    last_name = data.get('lastName', 0)
    pass1 = data.get('password1', 0)
    pass2 = data.get('password2', 0)
    
    if len(email) < 3:
        flash('Email to short!', category='error')
    elif len(name) < 3:
        flash('First Name to short!', category='error')
    elif len(last_name) < 1:
        flash('Last Name can not be empty!', category='error')
    elif pass1 != pass2:
        flash('Passwords not the same', category='error')
    elif len(pass1) < 4:
        flash('Passwords is too short', category='error')
    else:
        password = generate_password_hash(pass1, method="sha256")
        user = User(email = email, password = password, first_name = name, last_name = last_name)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', category='success')
        login_user(user, remember=True)
        return True
#endregion

#region Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password!', category='error')
        else:
            flash('User does not exist!', category='error')

    return render_template('login.html', user=current_user)

#endregion

#region Logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

#endregion