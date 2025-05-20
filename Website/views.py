import os, sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from datetime import date
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from .models import Customer, Professional, Admin, Service, ServiceRequest,  Review, ProfessionalRequest
from sqlalchemy import func

from . import db 
import json
views = Blueprint('views', __name__)


def calculate_avg_rating():
    avg_rating = db.session.query(func.avg(Review.rating)).scalar()
    return avg_rating if avg_rating is not None else 0  # Return 0 if no ratings exist


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    professionals = Professional.query.all()
    services = Service.query.all()
    service_requests = ServiceRequest.query.all()
    service_types = {service.type for service in services}
    reviews = Review.query.all()
    
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.admin_dashboard'))
    elif isinstance(current_user, Customer):
        return render_template('home.html', user=current_user, services=services, service_requests=service_requests, service_types=service_types)
    elif isinstance(current_user, Professional):
        return render_template('home-professional.html', user=current_user, services=services, service_requests=service_requests, reviews=reviews)
    else:
        return redirect(url_for('auth.login'))

@views.route('/search', methods=['GET'])
def search():
    search_by = request.args.get('search-by')
    search_text = request.args.get('search-text')
    results = []

    user_type=""
    if isinstance(current_user, Admin):
        user_type = "Admin"
    elif isinstance(current_user, Professional):
        user_type = "Professional"
    elif isinstance(current_user, Customer):
        user_type = "Customer"

    if search_by == 'service_request':
        results = ServiceRequest.query.filter(
            ServiceRequest.id.like(f"%{search_text}%") |
            ServiceRequest.remarks.like(f"%{search_text}%") |
            ServiceRequest.service.has(Service.type.like(f"%{search_text}%"))
        ).all()
    elif search_by == 'services':
        results = Service.query.filter(
            Service.name.like(f"%{search_text}%") |
            Service.type.like(f"%{search_text}%")
        ).all()
    elif search_by == 'pincode':
        results = Customer.query.filter(
            Customer.pincode.like(f"%{search_text}%")
        ).all()
    elif search_by == 'service-type':
        results = Service.query.filter(
            Service.type.like(f"%{search_text}%")
        ).all()
    elif search_by == 'customers':
        results = Customer.query.filter(
            Customer.name.like(f"%{search_text}%") |
            Customer.email.like(f"%{search_text}%")
        ).all()
    elif search_by == 'professionals':
        results = Professional.query.filter(
            Professional.name.like(f"%{search_text}%") |
            Professional.email.like(f"%{search_text}%")
        ).all()

    return render_template('search.html',user=current_user,user_type=user_type, results=results, search_by=search_by)

@views.route('/services/<string:type_name>')
def get_services(type_name):
    services = Service.query.filter_by(type=type_name).all()  # Filter by type
    services_list = [{'id': service.id, 'name': service.name, 'description': service.description, 'price': service.price} for service in services]
    return jsonify(services_list)

@views.route('/book_service/<int:service_id>', methods=['POST'])
def book_service(service_id):
    if isinstance(current_user, Customer):
        new_service_request = ServiceRequest(
            service_id=service_id,
            customer_id=current_user.id,
            date_of_request=datetime.utcnow().date(),
            service_status='requested'
        )
        
        # Add to the database session
        db.session.add(new_service_request)
        db.session.commit()  

        
    return redirect(url_for('views.home'))

@views.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    if isinstance(current_user, Professional):
        service_request = ServiceRequest.query.get(request_id)
        if service_request:
            service_request.service_status = 'assigned'
            service_request.professional_id = current_user.id
            db.session.commit()
        else:
            # Log an error or handle it as needed
            flash('Service request not found.', 'error') 

    return redirect(url_for('views.home'))


@views.route('/cancel_request/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    if isinstance(current_user, Customer):
        service_request = ServiceRequest.query.get(request_id)
        if service_request:
            # delete service request from DB
            db.session.delete(service_request)  # Delete the service request
            db.session.commit()  # Commit the changes
            flash('Service request successfully canceled.', 'success') 
            db.session.commit()
        else:
            # Log an error or handle it as needed
            flash('Service request not found.', 'error') 

    return redirect(url_for('views.home'))


@views.route('/submit_review/<int:request_id>', methods=['POST'])
def submit_review(request_id):
    service_req = ServiceRequest.query.get(request_id)
    rating = request.form.get('service_rating')
    comment = request.form.get('service_remarks')

    if service_req:
        
        new_review = Review(service_request_id=request_id, customer_id=current_user.id, rating=rating, comment=comment)
        db.session.add(new_review)
        service_req.service_status = 'closed'
        db.session.commit()
        
        flash("Review is Successfully submitted and Service  Request is now closed!", category="success")
    else:
        flash("Service request not found", category="error")

    return redirect(url_for('views.home'))


@views.route('/summary')
@login_required
def summary():
    count_requested = ServiceRequest.query.filter_by(service_status='requested').count() or 0
    count_assigned = ServiceRequest.query.filter_by(service_status='assigned').count() or 0
    count_closed = ServiceRequest.query.filter_by(service_status='closed').count() or 0

    status_dict = {
        'requested': count_requested,
        'assigned': count_assigned,
        'closed': count_closed
    }

    avg_rating = calculate_avg_rating()  # Assuming this function exists

    if isinstance(current_user, Admin):
        return redirect(url_for('admin.adm_summary'))
    elif isinstance(current_user, Customer):

        status_counts = {
            'requested': 0,
            'assigned': 0,
            'closed': 0
        }

        # Query for service requests related to the current user
        service_requests = ServiceRequest.query.filter(
            (ServiceRequest.customer_id == current_user.id)
        ).all()

        # Count the status of each service request
        for request in service_requests:
            status_counts[request.service_status] += 1

        return render_template('summary.html',user=current_user, status_dict=status_counts, avg_rating=avg_rating, user_type='Customer')
    elif isinstance(current_user, Professional):

        status_counts = {
            'requested': 0,
            'assigned': 0,
            'closed': 0
        }

        # Query for service requests where the current user is the professional
        service_requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == current_user.id
        ).all()

        # Count the status of each service request
        for request in service_requests:
            status_counts[request.service_status] += 1

        avg_rating = db.session.query(func.avg(Review.rating)).join(ServiceRequest).filter(
            ServiceRequest.professional_id == current_user.id
        ).scalar()

        return render_template('summary.html',user=current_user, status_dict=status_counts, avg_rating=avg_rating, user_type='Professional')
    
@views.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile():
    professional = Professional.query.get_or_404(current_user.id)

    # Update details from form
    professional.name = request.form.get('name')
    professional.email = request.form.get('email')
    professional.address = request.form.get('address')
    professional.pincode = request.form.get('pincode')
    professional.experience = request.form.get('experience')
    professional.service_type = request.form.get('service_type')

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('views.home'))