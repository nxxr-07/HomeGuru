from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import Customer, Professional, Admin, Service, ServiceRequest, Review, ProfessionalRequest
from Website import views
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    
    professionals = Professional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    professional_requests = ProfessionalRequest.query.all()
    
    return render_template('dashboard.html', 
                           user=current_user, 
                           professionals=professionals, 
                           services=services, 
                           service_requests=service_requests,
                           professional_requests=professional_requests,
                           count_professional_requests = len(professional_requests))



@admin_bp.route('/add_service', methods=['POST'])
@login_required
def add_service():
    name = request.form.get('service-name')
    desc = request.form.get('service-desc')
    type = request.form.get('service-type')
    price = request.form.get('service-baseprice')
    time_req = request.form.get('service-time')
    
    new_service = Service(name=name, description=desc, price = price, time_required = time_req, type=type)
    db.session.add(new_service)
    db.session.commit()
    flash('Service added successfully!', 'success')
    

    return redirect(url_for('admin.admin_dashboard'))

#Edit Service via Admin Portal
@admin_bp.route('/edit_service', methods=['POST'])
def edit_service():
    data = request.form
    service = Service.query.get(data['id'])
    if service:
        service.name = data['name']
        service.type = data['type']
        service.price = data['price']
        service.time_required = data['time_required']
        service.description = data['description']

        db.session.commit()  # Save changes to the database
        return jsonify(success=True)
    return jsonify(success=False)

@admin_bp.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False)


def calculate_avg_rating():
    avg_rating = db.session.query(func.avg(Review.rating)).scalar()
    return avg_rating if avg_rating is not None else 0  # Return 0 if no ratings exist


@admin_bp.route('/adm-summary')
def adm_summary():
    if isinstance(current_user, Admin):
        count_requested = ServiceRequest.query.filter_by(service_status='requested').count() or 0
        count_assigned = ServiceRequest.query.filter_by(service_status='assigned').count() or 0
        count_closed = ServiceRequest.query.filter_by(service_status='closed').count() or 0

        status_dict = {
            'requested': count_requested,
            'assigned': count_assigned,
            'closed': count_closed
        }

        avg_rating = calculate_avg_rating()  # Assuming this function exists

        return render_template('adm-summary.html',user=current_user, status_dict=status_dict, avg_rating=avg_rating)
    else:
        return redirect(url_for('views.home'))
    
@admin_bp.route('/approve/<int:request_id>', methods=['POST'])
def approve_professional_request(request_id):
    # Find the professional request
    prof_request = ProfessionalRequest.query.get_or_404(request_id)

    # Add to Professional table
    new_professional = Professional(
        name=prof_request.name,
        email=prof_request.email,
        password=prof_request.password,  # Ensure password is hashed during signup
        address=prof_request.address,
        pincode=prof_request.pincode,
        experience=prof_request.experience,
        service_type=prof_request.service_type
    )
    db.session.add(new_professional)

    # Delete from ProfessionalRequest table
    db.session.delete(prof_request)
    db.session.commit()

    flash(f'Professional Request {prof_request.name} approved.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/reject/<int:request_id>', methods=['POST'])
def reject_professional_request(request_id):
    # Find the professional request
    prof_request = ProfessionalRequest.query.get_or_404(request_id)

    # Delete from ProfessionalRequest table
    db.session.delete(prof_request)
    db.session.commit()

    flash(f'Professional Request {prof_request.name} rejected.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))