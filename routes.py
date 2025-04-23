from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, Transaction, Category, CategoryType
from forms import RegistrationForm, LoginForm, TransactionForm, FilterTransactionsForm, BudgetForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import extract, func
from datetime import datetime, timedelta, date
import calendar
import logging

# Home route - redirects to dashboard if logged in, otherwise shows landing page
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

# User logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get current month and year
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Get transactions for the current month
    month_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).all()
    
    # Calculate total income and expenses for the current month
    month_income = sum(t.amount for t in month_transactions if t.is_income)
    month_expenses = sum(t.amount for t in month_transactions if t.is_expense)
    month_balance = month_income - month_expenses
    
    # Get all transactions for the current year
    year_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.date) == current_year
    ).all()
    
    # Calculate yearly totals
    year_income = sum(t.amount for t in year_transactions if t.is_income)
    year_expenses = sum(t.amount for t in year_transactions if t.is_expense)
    year_balance = year_income - year_expenses
    
    # Get monthly data for charts
    monthly_data = db.session.query(
        extract('month', Transaction.date).label('month'),
        func.sum(Transaction.amount).label('amount'),
        Category.type
    ).join(Category).filter(
        Transaction.user_id == current_user.id,
        extract('year', Transaction.date) == current_year
    ).group_by(
        extract('month', Transaction.date),
        Category.type
    ).all()
    
    # Format data for Chart.js
    months_labels = [calendar.month_name[i] for i in range(1, 13)]
    income_data = [0] * 12
    expense_data = [0] * 12
    
    for item in monthly_data:
        month_idx = int(item.month) - 1  # Adjust for 0-based index
        if item.type == CategoryType.INCOME:
            income_data[month_idx] = float(item.amount)
        else:
            expense_data[month_idx] = float(item.amount)
    
    # Get category breakdown for pie chart
    category_data = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('amount'),
        Category.type
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == current_month,
        extract('year', Transaction.date) == current_year
    ).group_by(
        Category.name,
        Category.type
    ).all()
    
    # Format category data for Chart.js
    income_categories = []
    income_amounts = []
    expense_categories = []
    expense_amounts = []
    
    for item in category_data:
        if item.type == CategoryType.INCOME:
            income_categories.append(item.name)
            income_amounts.append(float(item.amount))
        else:
            expense_categories.append(item.name)
            expense_amounts.append(float(item.amount))
    
    # Budget alert
    budget_alert = None
    if current_user.monthly_budget > 0 and month_expenses > current_user.monthly_budget:
        budget_alert = f"Warning: You've exceeded your monthly budget of ₹{current_user.monthly_budget:.2f} by ₹{(month_expenses - current_user.monthly_budget):.2f}"
    
    # Recent transactions (last 5)
    recent_transactions = Transaction.query.filter_by(
        user_id=current_user.id
    ).order_by(Transaction.date.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                          title='Dashboard',
                          month_name=calendar.month_name[current_month],
                          month_income=month_income,
                          month_expenses=month_expenses,
                          month_balance=month_balance,
                          year_income=year_income,
                          year_expenses=year_expenses,
                          year_balance=year_balance,
                          months_labels=months_labels,
                          income_data=income_data,
                          expense_data=expense_data,
                          income_categories=income_categories,
                          income_amounts=income_amounts,
                          expense_categories=expense_categories,
                          expense_amounts=expense_amounts,
                          budget_alert=budget_alert,
                          current_year=current_year,
                          recent_transactions=recent_transactions)

# Transactions list
@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = FilterTransactionsForm()
    
    # Populate category dropdown
    form.category_id.choices = [(0, 'All Categories')] + [
        (c.id, c.name) for c in Category.query.order_by(Category.name).all()
    ]
    
    # Default values for filter
    filter_category_id = None
    start_date = None
    end_date = None
    
    if form.validate_on_submit():
        if form.category_id.data != 0:  # 0 means "All Categories"
            filter_category_id = form.category_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data
    
    # Build query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    if filter_category_id:
        query = query.filter_by(category_id=filter_category_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Execute query and order by date (newest first)
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return render_template('transactions.html', 
                          title='Transactions',
                          transactions=transactions,
                          form=form)

# Add transaction
@app.route('/transactions/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    
    # Dynamically update the category dropdown based on transaction type
    # The category dropdown will be populated via JavaScript
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            category_id=form.category_id.data,
            description=form.description.data,
            date=form.date.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions'))
    
    return render_template('add_transaction.html', 
                          title='Add Transaction',
                          form=form)

# API endpoint to get categories by type
@app.route('/api/categories/<type>')
@login_required
def get_categories_by_type(type):
    if type not in ['income', 'expense']:
        return jsonify({'error': 'Invalid type'}), 400
    
    cat_type = CategoryType.INCOME if type == 'income' else CategoryType.EXPENSE
    categories = Category.query.filter_by(type=cat_type).order_by(Category.name).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

# Edit transaction
@app.route('/transactions/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the transaction belongs to the current user
    if transaction.user_id != current_user.id:
        abort(403)
    
    form = TransactionForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.category_id = form.category_id.data
        transaction.description = form.description.data
        transaction.date = form.date.data
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions'))
    
    elif request.method == 'GET':
        form.amount.data = transaction.amount
        form.category_id.data = transaction.category_id
        form.description.data = transaction.description
        form.date.data = transaction.date
    
    return render_template('edit_transaction.html', 
                          title='Edit Transaction',
                          form=form,
                          transaction=transaction)

# Delete transaction
@app.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    # Create a form instance for CSRF validation
    form = FilterTransactionsForm()
    
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Ensure the transaction belongs to the current user
    if transaction.user_id != current_user.id:
        abort(403)
    
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

# Settings page
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    budget_form = BudgetForm()
    
    if budget_form.validate_on_submit():
        current_user.monthly_budget = budget_form.monthly_budget.data
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('settings'))
    
    elif request.method == 'GET':
        budget_form.monthly_budget.data = current_user.monthly_budget
    
    return render_template('settings.html', 
                          title='Settings',
                          budget_form=budget_form)
