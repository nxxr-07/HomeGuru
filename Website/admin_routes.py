from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from .models import Customer, Professional, Admin, Service, ServiceRequest
from Website import views
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    
    professionals = Professional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    
    return render_template('dashboard.html', user=current_user, professionals=professionals, services=services, service_requests=service_requests)
