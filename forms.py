from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, TextAreaField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from models import User, Category, CategoryType
from datetime import date

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose another one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be greater than 0")])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Add Transaction')

class FilterTransactionsForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[Optional()], default=0)
    start_date = DateField('From', validators=[Optional()])
    end_date = DateField('To', validators=[Optional()])
    submit = SubmitField('Filter')

class BudgetForm(FlaskForm):
    monthly_budget = FloatField('Monthly Budget', validators=[DataRequired(), NumberRange(min=0, message="Budget cannot be negative")])
    submit = SubmitField('Update Budget')
