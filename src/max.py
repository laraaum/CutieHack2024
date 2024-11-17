from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from isaac import Database  # Assuming your Database class is in database.py
import os
from datetime import datetime

# Initialize Database
db = Database()
app = db.app

# Session configuration
app.secret_key = os.getenv("SESSION_SECRET_KEY", "your-secret-key")

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Company access decorator
def company_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'error')
            return redirect(url_for('login'))
        
        user_data = db.db.collection('users').document(session['user_id']).get().to_dict()
        if not user_data.get('is_company', False):
            flash('Access denied. Company account required.', 'error')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Prepare additional data
        additional_data = {
            'username': request.form.get('username'),
            'is_company': request.form.get('is_company') == 'on',
            'company_name': request.form.get('company_name'),
            'region': request.form.get('region'),
            'request_ids_accepted': [],
            'account_bal': float(request.form.get('account_bal', 0)),
            'created_at': datetime.now().isoformat()
        }

        # Register user using your Database class
        user = db.register_user(email, password, additional_data)
        
        if user:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error creating account. Please try again.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Authenticate user using your Database class
        user = db.authenticate_user(email, password)
        
        if user:
            session['user_id'] = user['account']['ID']
            
            # Get user data to check type
            user_data = db.db.collection('accounts').document(user['account']['ID']).get().to_dict()
            
            flash('Logged in successfully!', 'success')
            
            # Redirect based on user type
            if user_data.get('is_company', False):
                return redirect(url_for('company_dashboard'))
            else:
                return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Generic dashboard route that redirects to the appropriate dashboard"""
    try:
        user_data = db.db.collection('users').document(session['user_id']).get().to_dict()
        if user_data.get('is_company', False):
            return redirect(url_for('company_dashboard'))
        return redirect(url_for('customer_dashboard'))
    except Exception as e:
        flash('Error accessing dashboard', 'error')
        return redirect(url_for('home'))

@app.route('/dashboard/company')
@login_required
@company_required
def company_dashboard():
    try:
        user_data = db.db.collection('users').document(session['user_id']).get().to_dict()
        return render_template('company_dashboard.html', user=user_data)
    except Exception as e:
        flash('Error accessing company dashboard', 'error')
        return redirect(url_for('home'))

@app.route('/dashboard/customer')
@login_required
def customer_dashboard():
    try:
        user_data = db.db.collection('users').document(session['user_id']).get().to_dict()
        return render_template('customer_dashboard.html', user=user_data)
    except Exception as e:
        flash('Error accessing customer dashboard', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)