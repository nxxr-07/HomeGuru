import os, sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from datetime import date
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from .models import Customer, Professional, Admin, Service, ServiceRequest,  Review

from . import db 
import json
views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.admin_dashboard'))
    elif isinstance(current_user, Customer):
        return render_template('home.html', user=current_user)
    elif isinstance(current_user, Professional):
        return render_template('home-professional.html', user=current_user)
    else:
        return redirect(url_for('auth.login'))






