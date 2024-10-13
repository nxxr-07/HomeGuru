from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
import requests
from bs4 import BeautifulSoup

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcdef'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .admin_routes import admin_bp  # Import admin routes

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from .models import Customer, Professional, Admin
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_type = session.get('user_type')  # Get user type from session
        if user_type == 'admin':
            return Admin.query.get(int(user_id))
        elif user_type == 'customer':
            return Customer.query.get(int(user_id))
        elif user_type == 'professional':
            return Professional.query.get(int(user_id))
        return None

    
    return app

def create_database(app):
    if not path.exists('Website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created database!')






