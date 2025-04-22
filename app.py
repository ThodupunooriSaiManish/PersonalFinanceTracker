import os
import logging
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)

# Generate a secure secret key if one is not provided
if not os.environ.get("SESSION_SECRET"):
    logging.warning("SESSION_SECRET not set in environment. Using a randomly generated key.")
generated_key = secrets.token_hex(16)
app.secret_key = os.environ.get("SESSION_SECRET", generated_key)

# Set the same key for CSRF protection
app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
app.config['WTF_CSRF_ENABLED'] = True

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Create database tables
with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models

    db.create_all()
    
    # Create default categories if they don't exist
    from models import Category, CategoryType
    
    # Check if we have any categories already
    if not db.session.query(models.Category).first():
        # Income categories
        income_categories = ['Salary', 'Freelance', 'Business', 'Investments', 'Other Income']
        for category in income_categories:
            db.session.add(models.Category(name=category, type=CategoryType.INCOME))
        
        # Expense categories
        expense_categories = ['Rent', 'Food', 'Shopping', 'Travel', 'Entertainment', 'Utilities', 'Education', 'Healthcare', 'Other Expense']
        for category in expense_categories:
            db.session.add(models.Category(name=category, type=CategoryType.EXPENSE))
        
        db.session.commit()
        logging.debug("Default categories created")

# Import routes (after db initialization to avoid circular imports)
from routes import *
