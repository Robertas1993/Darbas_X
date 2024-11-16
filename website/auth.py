import hashlib
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

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

from datetime import datetime, timedelta
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from .models import User, db

auth = Blueprint('auth', __name__)

from datetime import datetime, timedelta
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from .models import User, db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # Check if the user is blocked
        if user and user.blocked_until and datetime.utcnow() < user.blocked_until:
            remaining_time = user.blocked_until - datetime.utcnow()
            flash(f"Your login is blocked. Please try again in {remaining_time.seconds // 60} minutes.", "danger")
            return render_template('login.html', text="Please log in.", user=current_user)

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if user and user.password == hashed_password:
            # Successful login
            login_user(user)
            user.login_attempts = 0  # Reset login attempts on successful login
            user.blocked_until = None  # Clear block status
            db.session.commit()
            return redirect(url_for('views.home'))
        else:
            # User does not exist or password is incorrect
            if user:
                user.login_attempts += 1
                
                # Block user based on attempts
                if user.login_attempts == 3:
                    user.blocked_until = datetime.utcnow() + timedelta(minutes=5)
                elif user.login_attempts == 4:
                    user.blocked_until = datetime.utcnow() + timedelta(hours=1)
                elif user.login_attempts >= 5:
                    user.blocked_until = datetime.utcnow() + timedelta(hours=24)

                db.session.commit()
                flash(f"Your login has been blocked after {user.login_attempts} unsuccessful attempts. Please try again later.", "danger")
            else:
                flash("Invalid email or password.", "danger")

            return render_template('login.html', text="Invalid email or password.", user=current_user)

    return render_template('login.html', text="Please log in.", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

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
            hashed_password = hashlib.sha256(password1.encode()).hexdigest()

            new_user = User(email=email, first_name=first_name, password=hashed_password, Country=currency)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)  
            flash("Account was created successfully!", category="success")
            return redirect(url_for('views.home'))  

    return render_template("sign_up.html", user=current_user)


@auth.route("/delete", methods=['GET', 'POST'])
@login_required
def delete():
            
            db.session.delete(current_user)
            db.session.commit()

            logout_user()
            flash("The user been successfully deleted",category="success")

            return redirect(url_for('auth.login'))