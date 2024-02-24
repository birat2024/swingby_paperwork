from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os
import secrets
import logging

import pytz
from database import db
from flask_wtf import CSRFProtect



# Import the function to configure authentication from auth.py
from auth import configure_auth, get_selected_store_for_user, fetch_user_stores, get_user_stores
from models import GlobalSettings

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Load environment variables from a .env file
    load_dotenv()

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    ssl_certificate = os.getenv('SSL_CERTIFICATE')
    if ssl_certificate:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'ssl': {
                    'ssl_ca': ssl_certificate
                }
            }
        }

    app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(24))
    app.config['GOOGLE_MAPS_API_KEY'] = os.getenv('GOOGLE_MAPS_API_KEY')


    # Logging
    logging.basicConfig(level=logging.INFO)

    # Database Initialization
    db.init_app(app)

    # Register Blueprints
    from users.routes import users
    from terminal.routes import terminal
    from main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(terminal)
    app.register_blueprint(main)

    # Flask-Login Initialization
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'  # Adjust the endpoint as necessary
    login_manager.init_app(app)

    # Configure authentication (user loading)
    configure_auth(app, login_manager)

    

    csrf = CSRFProtect(app)
    
    @app.context_processor
    def global_context_processor():
        return {
            'get_selected_store_for_user': get_selected_store_for_user,
            'fetch_user_stores': fetch_user_stores,
            'get_user_stores': get_user_stores
        }

    @app.context_processor
    def inject_stores():
        if current_user.is_authenticated:
            user_stores, selected_store = fetch_user_stores(current_user)
            settings = GlobalSettings.query.first()  # Fetch global settings

            current_date_time = datetime.now()  # Get the current date and time in UTC

            # Apply the user's preferred timezone if available in global settings
            if settings and settings.default_timezone:
                timezone = pytz.timezone(settings.default_timezone)
                current_date_time = datetime.now(timezone)  # Convert to the user's preferred timezone

            return {
                'user_stores': user_stores,
                'selected_store': selected_store,
                'global_settings': settings,
                'current_date_time': current_date_time,
            }
        return {}


    return app  # This should be the only return statement at this indentation level



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
