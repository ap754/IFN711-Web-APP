from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pymysql
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'device_management_system'

# Database connection
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='987654321',
        db='device_management',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# Create tables if not exists
def init_db():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
            ''')
            
            # Create devices table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                asset_number VARCHAR(100) NOT NULL,
                asset_name VARCHAR(100) NOT NULL,
                asset_type VARCHAR(50) NOT NULL,
                purchase_cost FLOAT NOT NULL,
                purchase_date VARCHAR(50),
                estimated_purchase_date_range VARCHAR(100),
                details TEXT,
                asset_condition VARCHAR(50) NOT NULL,
                asset_storage INT NOT NULL
            )
            ''')
        conn.commit()
    finally:
        conn.close()

# Initialize database
init_db()

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('devices'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
                user = cursor.fetchone()
                
                if user:
                    session['username'] = username
                    return redirect(url_for('devices'))
                else:
                    flash('Invalid username or password', 'error')
        finally:
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username already exists
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                if cursor.fetchone():
                    flash('Username already exists', 'error')
                    return render_template('register.html')
                
                # Insert new user
                cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
                conn.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/devices')
def devices():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if search_query:
                # Search by asset number or asset name
                cursor.execute(
                    'SELECT * FROM devices WHERE asset_number LIKE %s OR asset_name LIKE %s',
                    (f'%{search_query}%', f'%{search_query}%')
                )
            else:
                cursor.execute('SELECT * FROM devices')
            
            devices = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('devices.html', devices=devices, search_query=search_query)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        asset_number = request.form['asset_number']
        asset_name = request.form['asset_name']
        asset_type = request.form['asset_type']
        purchase_cost = request.form['purchase_cost']
        know_exact_date = request.form.get('know_exact_date') == 'yes'
        
        purchase_date = None
        estimated_purchase_date_range = None
        
        if know_exact_date:
            purchase_date = request.form['purchase_date']
        else:
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            estimated_purchase_date_range = f"{start_date} to {end_date}"
        
        details = request.form['details']
        asset_condition = request.form['asset_condition']
        asset_storage = request.form['asset_storage']
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                INSERT INTO devices 
                (asset_number, asset_name, asset_type, purchase_cost, purchase_date, 
                estimated_purchase_date_range, details, asset_condition, asset_storage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    asset_number, asset_name, asset_type, purchase_cost, purchase_date,
                    estimated_purchase_date_range, details, asset_condition, asset_storage
                ))
                conn.commit()
                flash('Device added successfully!', 'success')
                return redirect(url_for('devices'))
        finally:
            conn.close()
    
    return render_template('add_device.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Get device information
    asset_number = str(data.get('asset_number', ''))
    condition = data.get('condition', '')
    asset_type = data.get('asset_type', '')
    purchase_date = data.get('purchase_date', '')
    estimated_purchase_date_range = data.get('estimated_purchase_date_range', '')
    
    # Calculate Age
    age = 0
    if purchase_date and purchase_date != 'None':
        # Extract year and calculate age
        year = int(purchase_date.split('-')[0])
        age = 2025 - year
    elif estimated_purchase_date_range and estimated_purchase_date_range != 'None':
        # Process estimated date range
        date_range = estimated_purchase_date_range
        if 'to' in date_range:
            parts = date_range.split('to')
            start_year = int(parts[0].strip().split('-')[0])
            end_year = int(parts[1].strip().split('-')[0])
            avg_year = (start_year + end_year) / 2
            age = 2025 - avg_year
    
    # Use model to predict price
    try:
        # Map function parameters to device information
        part_number = asset_number
        storage_type = asset_type
        
        # Create dataframe for prediction
        input_data = pd.DataFrame({
            'Age': [age],
            'Condition': [condition],
            'Storage Type': [storage_type],
            'Part Number': [part_number]
        })
        
        # Load model
        model_path = os.path.join(app.static_folder, 'models', 'price_model.pkl')
        pipeline = joblib.load(model_path)
        
        print(type(pipeline))
        # Try to bypass Pipeline and use components directly
        try:
            # Use separate components of the Pipeline for prediction
            preprocessor = pipeline.named_steps['preprocessor']
            regressor = pipeline.named_steps['regressor']
            
            # Manually preprocess and predict
            X_processed = preprocessor.transform(input_data)
            predicted_price = regressor.predict(X_processed)[0]
        except Exception as inner_e:
            print(f"Predict Error: {str(inner_e)}")
            # If the above method fails, try direct prediction
            predicted_price = pipeline.predict(input_data)[0]
        
        return jsonify({'price': float(predicted_price)})
    except Exception as e:
        print(f"Predict Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)