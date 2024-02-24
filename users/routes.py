
from datetime import datetime
from functools import wraps
import logging
import bcrypt
from flask import  current_app, render_template, request, flash, redirect, session, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user


import os
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import pytz
from auth import fetch_user_stores, get_user_stores
from users.forms import LoginForm, SettingsForm, SignUpForm

from models import GlobalSettings, Users, Store, ROLES
from database import db


from flask import Blueprint

users = Blueprint('users', __name__)




# Custom decorator to restrict access to owners
def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role == 'Owner':
            return f(*args, **kwargs)
        return redirect(url_for('users.login'))
    return decorated_function

# The manager_required and employee_required decorators can remain as updated above.

# Custom decorator to restrict access to managers
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role in ['Owner', 'Manager']:
            return f(*args, **kwargs)
        else:
            flash('Access denied. You need manager privileges.', 'danger')
            return redirect(url_for('users.login'))
    return decorated_function

# Custom decorator to restrict access to employees
def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.user_role in ['Employee', 'Manager', 'Owner']:
            return f(*args, **kwargs)
        else:
            flash('Access denied. You need employee privileges.', 'danger')
            return redirect(url_for('users.login'))
    return decorated_function

@users.route('/signup', methods=['GET', 'POST'])
@manager_required
def signup():
    # Create an instance of the SignUpForm
    form = SignUpForm()

    # Fetch all available stores from the 'store_name' table
    # This needs to be done before validating the form to ensure that
    # the 'stores' field in the form has its choices set.
    all_stores = Store.query.all()

    # Set the store choices for the SelectMultipleField
    # This assignment ensures that the form's 'stores' field has the
    # necessary choices available for validation and rendering.
    form.stores.choices = [(store.id, store.name) for store in all_stores]

    # Check if the form has been submitted and is valid
    if form.validate_on_submit():
        # Retrieve data from the form fields
        name = form.name.data
        email = form.email.data
        password = form.password.data
        selected_role = form.role.data
        selected_stores = form.stores.data  # List of selected store IDs

        # Check if the user already exists in the database
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address is already in use. Please use a different email.', 'danger')
            return redirect(url_for('users.signup'))

        # Hash the password before storing it in the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create the new user with the assigned role
        new_user = Users(name=name, email=email, password=hashed_password, user_role=selected_role)

        # Associate the selected stores with the new user
        for store_id in selected_stores:
            store = Store.query.get(store_id)
            if store:
                new_user.stores.append(store)

        # Add the user to the database and commit the transaction
        db.session.add(new_user)
        db.session.commit()

        flash('User registration successful!', 'success')
        return redirect(url_for('users.login'))

    # Render the signup form template with the populated form
    return render_template('signup.html', form=form, all_stores=all_stores)


@users.route('/login', methods=['GET', 'POST'])
def login():
    # Create an instance of your login form
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Query the user from the database using the provided email
        user = Users.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)  # Log in the user using Flask-Login

            flash('Login successful!', 'success')
            return redirect(url_for('terminal.dashboard'))  # Redirect to dashboard upon successful login

        else:
            flash('Login failed. Please check your credentials.', 'danger')

    return render_template('login.html', form=form)

def is_logged_in():
    return 'user_id' in session



@users.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.index'))



@users.route('/select_store/<int:store_id>')
@employee_required
def select_store(store_id):
    user = current_user
    user_stores = get_user_stores(user)

    print("Debug: User's stores:", [store.id for store in user_stores])  # Debug print

    if store_id not in [store.id for store in user_stores]:
        flash('You do not have access to this store.', 'danger')
        print("Debug: User does not have access to store ID", store_id)  # Debug print
        return redirect(url_for('terminal.dashboard'))

    try:
        session['selected_store'] = store_id
        user.selected_store_id = store_id
        db.session.commit()
        flash('Store selected successfully!', 'success')
        print("Debug: Store selected:", store_id)  # Debug print
    except Exception as e:
        logging.error(f"Error selecting store for user {user.id}: {e}")
        flash('An error occurred. Please try again.', 'danger')
        print("Debug: Error in selecting store:", e)  # Debug print

    return redirect(url_for('terminal.dashboard'))

# Default TImezone

@users.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    settings_record = GlobalSettings.query.first()

    if form.validate_on_submit():
        if not settings_record:
            settings_record = GlobalSettings()

        settings_record.default_timezone = form.default_timezone.data

        try:
            db.session.add(settings_record)
            db.session.commit()
            flash('Settings updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error('Failed to update settings: %s', str(e))
            flash(f'Failed to update settings: {e}', 'danger')

        return redirect(url_for('users.settings'))

    elif settings_record:
        form.default_timezone.data = settings_record.default_timezone

    return render_template('settings.html', form=form)