import hashlib
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db

# Initialize the Blueprint
auth = Blueprint('auth', __name__)

# Login Route
from flask import session, request, redirect, url_for, render_template
from datetime import datetime, timedelta
import hashlib
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, current_user
from .models import User
from . import db
import hashlib
from datetime import datetime, timedelta, timezone

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Patikrinkite vartotoją
        user = User.query.filter_by(email=email).first()  # Gauti vartotoją pagal el. paštą

        # Patikrinkite, ar vartotojas yra užblokuotas
        if user and user.blocked_until and datetime.utcnow() < user.blocked_until:
            remaining_time = user.blocked_until - datetime.utcnow()
            return f"Your login is blocked. Please try again in {remaining_time.seconds // 60} minutes."

        # Hash the password for checking
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if user and user.password == hashed_password:  # Check password only if user exists
            login_user(user)  # Naudojame Flask-Login, kad prisijungtume vartotoją
            user.blocked_until = None  # Atstatykite blokavimą, jei sėkmingai prisijungė
            user.login_attempts = 0  # Atstatykite bandymų skaičių
            db.session.commit()  # Išsaugokite pakeitimus
            return redirect(url_for('views.home'))  # Pakeiskite į savo namų maršrutą
        else:
            if user:
                # Padidinkite login attempts
                user.login_attempts += 1
                
                if user.login_attempts >= 3:
                    # Blokuokite prisijungimą 15 minučių
                    user.blocked_until = datetime.utcnow() + timedelta(minutes=15)
                    db.session.commit()  # Išsaugokite pakeitimus
                    return "Your login has been blocked after 3 unsuccessful attempts. Please try again in 15 minutes."
                
                db.session.commit()  # Išsaugokite pakeitimus po bandymo skaičiaus didinimo
            return render_template('login.html', text="Invalid email or password.", user=current_user)
    
    return render_template('login.html', text="Please log in.", user=current_user)




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


@auth.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
            
            db.session.delete(current_user)
            db.session.commit()

            logout_user()
            flash("The user been successfully deleted",category="success")

            return redirect(url_for('auth.login'))