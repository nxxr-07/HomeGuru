from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

class Admin(db.Model, UserMixin):
    __tablename__ = 'Admin'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    
    def __repr__(self):
        return f'<Admin {self.name}>'

class Customer(db.Model, UserMixin):
    __tablename__ = 'Customer'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Customer {self.name}>'

class Professional(db.Model, UserMixin):
    __tablename__ = 'Professional'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(40), nullable=False)
    address = db.Column(db.String(255))
    pincode = db.Column(db.String(10))
    experience = db.Column(db.Integer)
    service_type = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)



class Service(db.Model):
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=True)  # e.g. "2 hours"
    description = db.Column(db.Text, nullable=True)




class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('Professional.id'), nullable=True)  # Optional until assigned
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.Enum('requested', 'assigned', 'closed'), default='requested')
    remarks = db.Column(db.Text, nullable=True)

    service = db.relationship('Service', backref='service_requests')
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    professional = db.relationship('Professional', foreign_keys=[professional_id])


class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.id'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g. 1 to 5 stars
    comment = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship('Customer', backref='reviews')
    service_request = db.relationship('ServiceRequest', backref='reviews')

