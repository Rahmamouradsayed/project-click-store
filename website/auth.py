from flask import Blueprint, render_template, flash, redirect, request, url_for, session
from .classes import Customer, Product
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import secrets
from flask import current_app
from authlib.integrations.flask_client import OAuth
import json 

auth = Blueprint('auth', __name__)


def generate_csrf_token():
    token = secrets.token_hex(16)
    session['csrf_token'] = token
    return token


def validate_csrf_token():
    token = session.get('csrf_token')
    if not token or token != request.form.get('csrf_token'):
        raise ValueError("CSRF token is invalid or missing.")

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        validate_csrf_token() 

        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        
        if password1 != password2:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')

        
        if len(password1) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('signup.html')

   
        if len(username) < 5 or len(username) > 20:
            flash('Username must be between 5 and 20 characters long.', 'error')
            return render_template('signup.html')

        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email already exists. Please login or use another email.', 'error')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password1, method='scrypt')
        new_customer = Customer(email=email, username=username, password_hash=hashed_password)
        db.session.add(new_customer)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

   
    session['csrf_token'] = generate_csrf_token()
    return render_template('signup.html', csrf_token=session['csrf_token'])

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            validate_csrf_token()  
            email = request.form.get('email')
            password = request.form.get('password')

            customer = Customer.query.filter_by(email=email).first()

            if customer and check_password_hash(customer.password_hash, password):
                login_user(customer)
                flash('Login successful!', 'success')
                return redirect('/')
            else:
                flash('Incorrect email or password. Please try again.', 'error')
        except ValueError as e:
            flash(str(e), 'error')

    session['csrf_token'] = generate_csrf_token()
    return render_template('login.html', csrf_token=session['csrf_token']) 

@auth.route('/logout', methods=['GET'])
@login_required
def log_out():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect('/')




@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    if current_user.id != customer_id:
        flash('Unauthorized access!', 'error')
        return redirect('/')

    customer = Customer.query.get_or_404(customer_id)
    return render_template('profile.html', customer=customer)



@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    if current_user.id != customer_id:
        flash('Unauthorized access!', 'error')
        return redirect('/')

    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        try:
            validate_csrf_token()

            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')

            if not check_password_hash(customer.password_hash, current_password):
                flash('Current password is incorrect!', 'error')
            elif new_password != confirm_new_password:
                flash('New passwords do not match!', 'error')
            else:
                if len(new_password) < 8:
                    flash("Password must be at least 8 characters long", 'error')
                else:
                    customer.password_hash = generate_password_hash(new_password, method='scrypt')
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                    return redirect(url_for('auth.profile', customer_id=customer.id))
        except ValueError as e:
            flash(str(e), 'error')

    session['csrf_token'] = generate_csrf_token()
    return render_template('change_password.html', csrf_token=session['csrf_token'])



@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        try:
            validate_csrf_token()
            email = request.form.get('email')
            customer = Customer.query.filter_by(email=email).first()
            if customer:
                customer.reset_token_used = False
                db.session.commit()
                token = generate_reset_token(email)
                reset_link = url_for('auth.reset_password', token=token, _external=True)
                message = Message('Password Reset Request',
                                  sender='clickstore.official65@gmail.com',
                                  recipients=[email])
                message.body = f'Click the following link to reset your password: {reset_link}'
                mail.send(message)
                flash('A password reset link has been sent to your email address.')
                return redirect(url_for('auth.login'))
            else:
                flash('No account found with that email address.')
        except ValueError as e:
            flash(str(e), 'error')

    session['csrf_token'] = generate_csrf_token()
    return render_template('reset_password_request.html', csrf_token=session['csrf_token'])


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email)


def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, max_age=max_age)
    except Exception:
        return None
    return email


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if email:
        customer = Customer.query.filter_by(email=email).first()
        if not customer:
            flash('No account found for this token.')
            return redirect(url_for('auth.reset_password_request'))

        if customer.reset_token_used:
            flash('This password reset token has already been used.')
            return redirect(url_for('auth.reset_password_request'))

        if request.method == 'POST':
            try:
                validate_csrf_token()
                new_password = request.form.get('new_password')
                if not new_password:
                    flash("Please enter a new password", 'error')
                elif len(new_password) < 6:
                    flash("Password must be at least 6 characters long", 'error')
                else:
                    customer.password_hash = generate_password_hash(new_password)
                    customer.reset_token_used = True
                    db.session.commit()
                    flash('Your password has been reset successfully.', 'success')
                    return redirect(url_for('auth.login'))
            except ValueError as e:
                flash(str(e), 'error')

        return render_template('reset_password.html', token=token, csrf_token=session.get('csrf_token'))
    else:
        flash('The password reset token is either invalid or expired.')
        return redirect(url_for('auth.reset_password_request'))

