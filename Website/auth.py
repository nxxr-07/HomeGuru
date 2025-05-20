from flask import Blueprint, render_template, request, flash, redirect , url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from Website import views
from .models import Customer, Professional, Admin, Service, ProfessionalRequest
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        
        admin  = Admin.query.filter_by(email=email).first()
        customer = Customer.query.filter_by(email=email).first()
        professional = Professional.query.filter_by(email=email).first()

        if customer:
            if check_password_hash(customer.password, password):
                flash('Logged in Successfully!', category='success')
                login_user(customer, remember=True)
                session['user_type'] = 'customer'
                return redirect(url_for('views.home', user=customer))
            else:
                flash('Incorrect Password, Try again.', category='error')
        elif professional:
            if check_password_hash(professional.password, password) or professional.password == password:
                flash('Logged in Successfully!', category='success')
                login_user(professional, remember=True)
                session['user_type'] = 'professional'
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password, Try again.', category='error')
        elif admin:
            if admin.password == password:
                flash('Logged in Successfully!', category='success')
                login_user(admin, remember=True)
                session['user_type'] = 'admin'
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Incorrect Password, Try again.', category='error')

        else:
            flash('Invalid Email',category='error')

            

    return render_template("login.html", user=0)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_type', None)
    return redirect(url_for('auth.login'))

@auth.route("/sign-up-customer", methods=['GET', 'POST'])
def sign_up_customer():

    
    if request.method=="POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        address = request.form.get('address')
        pin = request.form.get('pincode')
        

        customer = Customer.query.filter_by(email=email).first()
        if customer:
            flash('Email already exists', category='error')
        if(len(email))<4:
            flash('Email Must be greater than 4 characters', category="error")
        elif len(name) < 2:
            flash('First Name Must be greater than 3 characters', category="error")
        elif( len(password))<7:
            flash('Password Must be greater than 7 characters', category="error")
        else:
            new_user = Customer(email=email, name = name, password=generate_password_hash(password), pincode=pin, address=address)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)

            flash("Account Created", category="success")
            return redirect(url_for('views.home'))
    
    return render_template("sign_up_customer.html")



@auth.route("/sign-up-professional", methods=['GET', 'POST'])
def sign_up_professional():
    services = Service.query.all()

    if request.method=="POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        address = request.form.get('address')
        pin = request.form.get('pincode')
        experience = request.form.get('experience')
        service_type = request.form.get('serviceType')
        
      
        professional = Professional.query.filter_by(email=email).first()

        if professional :
            flash('Email already exists', category='error')
        if(len(email))<4:
            flash('Email Must be greater than 4 characters', category="error")
        elif len(name) < 2:
            flash('First Name Must be greater than 3 characters', category="error")
        elif( len(password))<7:
            flash('Password Must be greater than 7 characters', category="error")
        else:
            new_user = ProfessionalRequest(email=email, name = name, password=password, pincode=pin, address=address, experience=experience, service_type=service_type)
            db.session.add(new_user)
            db.session.commit()

            flash("Professioal Request Submitted For Admin Approval", category="success")
            return redirect(url_for('views.home'))
    
    return render_template("sign_up_professional.html", services=services)


    
@auth.route('/register_professional', methods=['POST'])
def register_professional():
   
    return redirect(url_for('admin.admin_dashboard')) 