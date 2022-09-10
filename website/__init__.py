from flask import Flask
import os
from .views import views
from .auth import auth
from .models import db, db_name, User, Note, Comment
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdfasdfadsf'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    db.init_app(app)
     
    app.register_blueprint(views,  url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    start_db(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app    

def start_db(app):
    if not os.path.exists(f'website\{db_name}'):
        db.create_all(app = app)
        print('Created new DB!')
    else:
        print('Connected to DB')
