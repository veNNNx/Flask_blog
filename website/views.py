import os, secrets
from pathlib import Path
from datetime import datetime
import configparser
from fileinput import filename
import requests
from urllib.request import Request
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import Note, db, Comment, User, Like
import json, datetime
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
views = Blueprint('views', __name__, template_folder="templates")

#region HOME

@views.route('/', methods = ['POST', 'GET'])
@login_required
def home():
    all_not = Note.query.all()
    check_activity()
    return render_template("home.html", user = current_user, notes = all_not)

@views.route('/create-note', methods = ['POST'])
@login_required
def create_note():
    if request.method == 'POST':
        title = request.form.get('title')
        note = request.form.get('note')
        if note:
            new_note = Note(title = title, text = note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added', category='success')
    return redirect(url_for('views.home'))
    

@views.route('/create-comment/<note_id>', methods = ['POST'])
@login_required
def create_comment(note_id):
    if request.method == 'POST':
        comm = request.form.get('comment')
        if not comm:
            flash('Comment cant be empty!')
        else:
            note = Note.query.filter_by(id = note_id)
            if not note:
                flash('Failed!')
            else:
                new_comm = Comment(text = comm, user_id=current_user.id, note_id=note_id)
                db.session.add(new_comm)
                db.session.commit()
                flash('Comment added!', category='success')
    return redirect(url_for('views.home'))

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id or current_user.id == 1:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id or current_user.id == 1:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route('/like-post/<int:id>', methods=['GET'])
def like(id):
    note = Note.query.get(id)
    like = Like.query.filter_by(user_id=current_user.id, note_id=id).first()
    if note:
        if not like:
            new_like = Like(user_id=current_user.id, note_id=id)
            db.session.add(new_like)
            db.session.commit()
        elif like:
            db.session.delete(like)
            db.session.commit()
    return redirect(url_for('views.home'))

#endregion

#region PROFILE
@views.route('/profile/<int:id>', methods = ['POST', 'GET'])
@login_required
def profile(id=None):
    check_activity()
    if not id:
        user = current_user
    else:
        user = User.query.get(id)
    print(user)
    image_profile = url_for('static', filename='profile_img/' + user.picture)
    return render_template("profile.html", user = user, image_profile = image_profile, current_user = current_user)

@views.route('/update-profile/<int:id>', methods = ['POST', 'GET'])
@login_required  
def update_profile(id):
    if request.method == 'POST':
        data = request.form
        current_user.first_name = data.get('firstName', 0)
        current_user.last_name = data.get('lastName', 0)
        current_user.lat = data.get('lat', 0)
        current_user.lot = data.get('lot', 0)
        if request.files['picture']:
            picture = save_picture(request.files['picture'])
            current_user.picture = picture

        current_user.date_modified = datetime.datetime.utcnow().replace(microsecond=0)
        if len(current_user.first_name) < 3:
            flash('First Name to short!', category='error')
        else:
            #TO DO hash passwords
            db.session.commit()
            flash('User updated!', category='success')
    return redirect(url_for('views.profile', id = current_user.id))

def save_picture(file):
    prefix = secrets.token_hex(8)
    filename = prefix + file.filename
    path_to_project = str(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')
    file.save(os.path.join(path_to_project+'/static/profile_img/', filename))
    return filename

@views.route('/update-password/<id>', methods = ['POST', 'GET'])
@login_required 
def update_password(id):
    if request.method == 'POST':
        data = request.form
        pass1 = data.get('password1', 0)
        pass2 = data.get('password2', 0)
        control = data.get('control_password', 0)
        if not check_password_hash(current_user.password, control):
            flash('Wrong confirmation password!', category='error')
        elif pass1 != pass2:
            flash('Passwords not the same!', category='error')
        elif len(pass1) < 4:
            flash('Passwords is too short!', category='error')
        else:
            password = generate_password_hash(pass1, method="sha256")
            current_user.password = password 
            db.session.commit()
            flash('Password updated!', category='success')
    return redirect(url_for('views.profile', id = current_user.id))

@views.route('/delete-profile/<id>', methods = ['POST', 'GET'])
@login_required
def delete_profile(id):
    user_to_delete = User.query.get(id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted', category='error')
    return redirect(url_for('views.home'))
#endregion

#region USERS
@views.route('/users', methods = ['POST', 'GET'])
@login_required  
def users():
    check_activity()
    all_users = User.query.order_by(desc(User.last_active)).all()
    return render_template("users.html", user = current_user, users = all_users)
#endregion

@login_required  
def check_activity():
    current_user.last_active = datetime.datetime.now().replace(microsecond=0)
    db.session.commit()


#region WEATHER


@views.route('/weather', methods = ['POST', 'GET'])
@login_required
def weather():
    data = get_weather_data()
    if data:
        sunset = int(data['sys']['sunset'])
        sunrise = int(data['sys']['sunrise'])
        timezone = int(data['timezone'])
        sunset = get_time(sunset, timezone)
        sunrise = get_time(sunrise, timezone)
        data["main"]["temp"] = "{:.2f}".format(data["main"]["temp"] - 273.15)
    else:
        sunrise = sunset = None
    return render_template("weather.html", user = current_user, data = data, sunrise = sunrise, sunset = sunset)

def get_time(timestamp, timezone):
    return datetime.datetime.fromtimestamp(timestamp + timezone).strftime('%H:%M:%S')

def get_weather_data():
    api_key = get_api_key()
    lat = current_user.lat
    lon = current_user.lon
    api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    print(api_url)
    r = requests.get(api_url)
    if r.status_code >= 400:
        print(r.text)
        return None
    return r.json()

def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']

@views.route('/send_lat_lon', methods = ['POST'])
@login_required
def get_lat_lon_data():
    data = json.loads(request.data)
    lat = data['lat']
    lon = data['lon']
    current_user.lat = lat
    current_user.lon = lon
    db.session.commit()
    return jsonify({})
#endregion