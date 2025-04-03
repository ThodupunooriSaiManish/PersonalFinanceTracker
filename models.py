from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Budget limit for alert functionality
    monthly_budget = db.Column(db.Float, default=0.0)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class CategoryType(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(SQLAlchemyEnum(CategoryType), nullable=False)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    
    def __repr__(self):
        return f"Category('{self.name}', '{self.type}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    def __repr__(self):
        return f"Transaction('{self.amount}', '{self.date}', '{self.category.name}')"
    
    @property
    def is_expense(self):
        return self.category.type == CategoryType.EXPENSE
    
    @property
    def is_income(self):
        return self.category.type == CategoryType.INCOME
