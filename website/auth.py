import hashlib
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db

# Initialize the Blueprint
auth = Blueprint('auth', __name__)

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if login attempts are blocked
        if session.get('login_attempts', 0) >= 3:
            return "Your login has been blocked after 3 unsuccessful attempts. Please try again later."

        # Hash the password for checking
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check user credentials
        user = User.query.filter_by(email=email, password=hashed_password).first()
        
        if user:
            login_user(user)  # Use Flask-Login to log in the user
            session['login_attempts'] = 0  # Reset login attempts on successful login
            return redirect(url_for('views.home'))  # Adjust to your home route
        else:
            # Increment login attempts
            session['login_attempts'] = session.get('login_attempts', 0) + 1
            return render_template('login.html', text="Invalid email or password.")
    
    return render_template('login.html', text="Please log in.", user=session.get('user'))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Sign-up Route
@auth.route("/sign-up", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        currency = request.form.get('country-selector')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email already exists", category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 2 characters.', category='error')
        elif not re.match(r'^[a-zA-Z0-9_]*$', first_name):
            flash('First name can\'t have special characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Hash the password
            hashed_password = hashlib.sha256(password1.encode()).hexdigest()

            new_user = User(email=email, first_name=first_name, password=hashed_password, Country=currency)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)  # Log in the new user
            flash("Account was created successfully!", category="success")
            return redirect(url_for('views.home'))  # Adjust to your home route

    return render_template("sign_up.html", user=current_user)