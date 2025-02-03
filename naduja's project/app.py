#Naduja Mohamed  studentid:23027771
#from app import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
#mport pymsql
import mysql.connector
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf import FlaskForm
#from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators, Form, HiddenField
from wtforms.validators import DataRequired, Regexp
import os
from datetime import datetime
#from itsdangerous import URLSafeSerializer
#from passlib.hash import pbkdf2_sha256
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)
app.secret_key = 'your_secret_key_here' 

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'naduja12_09'
app.config['MYSQL_DATABASE_DB'] = 'hoteldb'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

def get_db_connection():
    conn = mysql.connector.connect(
        user=app.config['MYSQL_DATABASE_USER'],
        password=app.config['MYSQL_DATABASE_PASSWORD'],
        host=app.config['MYSQL_DATABASE_HOST'],
        database=app.config['MYSQL_DATABASE_DB']
    )
    return conn


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/bristol')
def bristol():
    # Render Belfast hotels page
    return render_template('bristol.html')



@app.route('/london')
def london():
    # Render Belfast hotels page
    return render_template('london.html')




@app.route('/belfast')
def belfast():
    # Render Belfast hotels page
    return render_template('belfast.html')

@app.route('/swansea')
def swansea():
    # Render Swansea hotels page
    return render_template('swansea.html')

@app.route('/plymouth')
def plymouth():
    # Render Plymouth hotels page
    return render_template('plymouth.html')

@app.route('/newcastle')
def newcastle():
    # Render Newcastle hotels page
    return render_template('newcastle.html')

@app.route('/cardiff')
def cardiff():
    # Render Cardiff hotels page
    return render_template('cardiff.html')

@app.route('/birmingham')
def birmingham():
    # Render Birmingham hotels page
    return render_template('birmingham.html')





@app.route('/payment_form', methods=['GET', 'POST'])
def payment_form():
    if 'user_id' not in session:
        flash("You need to log in first!")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process payment form data (simulated)
        # Assuming payment is successful
        # You can implement actual payment processing logic here
        # After successful payment, redirect to booking receipt with a success message
        flash("Payment successful!")
        return redirect(url_for('booking_receipt'))  

    return render_template('payment_form.html')



@app.route('/booking_receipt')
def booking_receipt():
    if 'user_id' not in session:
        flash("You need to log in first!")
        return redirect(url_for('login'))

    # Here you can fetch the details of the first selected room from the database
    # For demonstration purposes, I'll simulate the data

    # Simulated room data
    room = {
        'id': 1,
        'room_type': 'Standard Room',
        'features': 'WiFi, TV, Mini-bar',
        'description': 'A comfortable room for one guest.',
        'image': 'standard_room.jpg'
    }

    return render_template('booking_receipt.html', room=room)
    
@app.route('/booking_form', methods=['POST'])
def booking_form():
    city_name = request.form.get('city_name')
    room_type = request.form.get('room_type')

    # Filter hotels based on selected city and room type
    filtered_hotels = [hotel for hotel in hotel if hotel['city'] == city_name and hotel['room_type'] == room_type]

    return render_template('booking_form.html', hotels=filtered_hotels)




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm']

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))  # Redirect back to registration form

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT username FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists', 'error')
                return redirect(url_for('register'))  # Redirect back to registration form

            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()  # Commit only if all operations are successful
            flash('User registered successfully', 'success')
            return redirect(url_for('login'))  # Redirect to login page upon successful registration
        except mysql.connector.Error as e:
            conn.rollback()  # Rollback the transaction on error
            flash(f'Registration failed: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('register'))  # Redirect back to registration form in case of any failure

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT password FROM user WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user['password'] == password:
                # Password is correct
                session['user_id'] = username  # Store the username in session

                # Determine where to redirect after login
                next_url = request.args.get('next')
                if next_url and next_url == url_for('payment_form'):  # Check if the intent was to go to payment form
                    return redirect(url_for('login', next=url_for('payment_form')))  # Redirect to payment form if that was the intent
                else:
                    return redirect(url_for('user_dashboard'))  # Redirect to user dashboard if no specific intent
            else:
                # Password is incorrect or user does not exist
                flash("Invalid username or password.")
                return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()
    else:
        # If the request is GET, display the login page
        return render_template('login.html')


@app.route('/admin-login', methods=['POST', 'GET'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('admin_login'))  # Redirect to admin login page

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Adjust the SQL query to also retrieve the is_admin field
            cursor.execute("SELECT password, is_admin FROM user WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user['password'] == password and user['is_admin']:
                # Password is correct and user is an admin
                session['admin_id'] = username  # Store the admin username in session
                flash("Admin login successful!")
                return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
            else:
                # Password is incorrect, user is not an admin, or user does not exist
                flash("Invalid username or password, or not authorized.")
                return redirect(url_for('admin_login'))
        finally:
            cursor.close()
            conn.close()
    else:
        # If the request is GET, display the admin login page
        return render_template('admin_login.html')
    
#admin_logout
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_id', None)  # Clear the 'admin_id' from session
    flash('You have been logged out as admin.', 'info')
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the 'user_id' from session
    session.pop('admin_id', None)
    flash('You have been logged out') #set flash message
    return redirect(url_for('home'))

# Hardcoded hotel details for all 17 cities
hotel = [
    {"city": "Aberdeen", "capacity": 90, "peak_rate": 140, "off_peak_rate": 70},
    {"city": "Belfast", "capacity": 80, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Birmingham", "capacity": 110, "peak_rate": 150, "off_peak_rate": 75},
    {"city": "Bristol", "capacity": 100, "peak_rate": 140, "off_peak_rate": 70},
    {"city": "Cardiff", "capacity": 90, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Edinburgh", "capacity": 120, "peak_rate": 160, "off_peak_rate": 80},
    {"city": "Glasgow", "capacity": 140, "peak_rate": 150, "off_peak_rate": 75},
    {"city": "London", "capacity": 160, "peak_rate": 200, "off_peak_rate": 100},
    {"city": "Manchester", "capacity": 150, "peak_rate": 180, "off_peak_rate": 90},
    {"city": "New Castle", "capacity": 90, "peak_rate": 120, "off_peak_rate": 70},
    {"city": "Norwich", "capacity": 90, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Nottingham", "capacity": 110, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Oxford", "capacity": 90, "peak_rate": 180, "off_peak_rate": 90},
    {"city": "Plymouth", "capacity": 80, "peak_rate": 180, "off_peak_rate": 90},
    {"city": "Swansea", "capacity": 70, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Bournemouth", "capacity": 90, "peak_rate": 130, "off_peak_rate": 70},
    {"city": "Kent", "capacity": 100, "peak_rate": 140, "off_peak_rate": 80},
]

# Route to display the booking form

@app.route('/user_dashboard')
def user_dashboard():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("You need to log in first!")
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

@app.route('/view_booking')
def view_booking():
    return render_template('view_booking.html')

@app.route('/update_booking')
def update_booking():
    return render_template('update_booking.html')

@app.route('/cancel_booking')
def cancel_booking():
    return render_template('cancel_booking.html')


@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/terms_and_conditions')
def terms_and_conditions():
    return render_template('terms_and_conditions.html')

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        # Process the form data here (save to database, send email, etc.)
        # For demonstration purposes, let's assume the form data is processed successfully

        # Redirect to a confirmation page or render the same page with a message
        return redirect(url_for('contact_confirmation'))

    # If it's a GET request or initial load, render the contact form page
    return render_template('contact_us.html')

@app.route('/contact/confirmation')
def contact_confirmation():
    return render_template('contact_confirmation.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Ensure the admin is logged in
    if 'admin_id' not in session:
        flash("You need to log in as an admin first!")
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_manage_users')
def admin_manage_users():
    # Placeholder for managing users
    return render_template('admin_manage_users.html')

@app.route('/admin_manage_hotels')
def admin_manage_hotels():
    # Placeholder for managing hotels
    return render_template('admin_manage_hotels.html')

@app.route('/admin_manage_room_status')
def admin_manage_room_status():
    # Placeholder for managing room status
    return render_template('admin_manage_room_status.html')

@app.route('/admin_view_reports')
def admin_view_reports():
    # Placeholder for viewing reports
    return render_template('admin_view_reports.html')


if __name__ == '__main__':
    app.run(debug=True)