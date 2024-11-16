from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import re
import os
import datetime
from isaac import Database

max = Flask(__name__)

@max.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Basic server-side validation
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
            
        # Register user with additional data
        additional_data = {
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }
        
        company_data = {
            'is_company': True,
            'company_name': 'Company XYZ Ltd',
            'region': 'US-West'
        }
        user = Database.register_user('company@example.com', 'secure_password', company_data)
        if user:
            session['user_id'] = user['localId']
            return redirect(url_for('calendar_view'))
        else:
            return render_template('signup.html', error="Registration failed. Please try again.")
            
    return render_template('signUpPage.html')

@max.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Database.authenticate_user(email, password)
        if user:
            session['user_id'] = user['localId']
            # Update last login time in Firestore
            # database.update_user(user['localId'], {'last_login': datetime.now().isoformat()})
            return redirect(url_for('calendar_view'))
        else:
            return render_template('login.html', error="Invalid login credentials")
    
    return render_template('logInPage.html')

@max.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

max.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))