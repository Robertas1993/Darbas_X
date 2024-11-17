from . import db # importing from the current package
from flask_login import UserMixin
from sqlalchemy.sql import func
import ast
from datetime import datetime
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime


class User(db.Model, UserMixin): #User Model - capital U because of python standarts
    id = db.Column(db.Integer,primary_key=True) #Id column counted by int with Primary Key!
    email = db.Column(db.String(150), unique=True, nullable=False) #unique - allows/forbids (False/True) multiple instances with same info 
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))
    cartItems = db.Column(db.String(150), default="Empty")
    Country = db.Column(db.String(150),nullable=False)
    comments = db.relationship('Comment', backref='user', lazy=True)
    blocked_until = db.Column(db.DateTime, nullable=True)    
    login_attempts = db.Column(db.Integer, default=0) 
    balance = db.Column(db.Float, default=0.0)  # Pridėkite balansą
    orders = db.relationship('Order', backref='user', lazy=True)
    is_verified = db.Column(db.Boolean, default=False)  # Pridėtas laukelis el. pašto patvirtinimui
    def getUserId(user):
        return user.id
    


def set_password(self, password):
        # Hash'iname slaptažodį
        self.password = hashlib.sha256(password.encode()).hexdigest()

def check_password(self, password):
        # Patikriname slaptažodį
        return self.password == hashlib.sha256(password.encode()).hexdigest()

class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    amountPaid = db.Column(db.Integer, nullable=False)
    orderItems = db.Column(db.String, nullable=False)
    orderDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # New column for order date
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    priceModifier = db.Column(db.Float, nullable=False, default=1)
    isOnSale = db.Column(db.Boolean, default=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_data = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def getPrice(component):
    return component.price
    
class Configuration:
    def __init__(self):
        self.environment = 'development'  # Ensure this line exists

config = Configuration()
print(config.environment)  # This should work if 'environment' is an instance attribute






    
