from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from flask_session import Session
import sqlite3
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key
Session(app)

# Get absolute path to the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'user_data.db')

# Initialize the SQLite database
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Create the 'users' table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     name TEXT, 
                     username TEXT UNIQUE, 
                     password TEXT, 
                     address TEXT, 
                     profession TEXT)''')
        conn.commit()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")
    finally:
        conn.close()

# Route to render the signup page
@app.route('/')
def signup_page():
    return render_template('signup.html')

# Route to render the login page
@app.route('/login')
def login_page():
    return render_template('login.html')

# Protected route for the doctor page
@app.route('/doctor')
def doctor_page():
    if 'user_id' not in session or session.get('profession') != 'doctor':
        logging.warning(f"Unauthorized access attempt to doctor page. Session: {session}")
        return redirect(url_for('login_page'))
    return render_template('doctor.html')

# Route to handle the signup form submission
@app.route('/signup', methods=['POST'])
def signup_user():
    try:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        profession = request.form['profession']

        logging.info(f"Received signup data: {name}, {username}, {address}, {profession}")

        # Validate username format
        if "@" not in username:
            logging.warning("Invalid username format.")
            return jsonify({"success": False, "message": "Invalid username format"})

        # Insert data into the users table
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        logging.info("Inserting user into database...")
        c.execute("INSERT INTO users (name, username, password, address, profession) VALUES (?, ?, ?, ?, ?)",
                  (name, username, password, address, profession))
 
        conn.commit()
        logging.info("User added successfully.")
        return redirect(url_for('login_page'))

    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error during signup: {e}")
        return jsonify({"success": False, "message": f"Username already taken: {e}"})
    except sqlite3.Error as e:
        logging.error(f"Database error during signup: {e}")
        return jsonify({"success": False, "message": f"Database error: {e}"})
    finally:
        if conn:
            conn.close()

# Route to handle the login form submission
@app.route('/login', methods=['POST'])
def login_user():
    try:
        username = request.form['username']
        password = request.form['password']

        logging.info(f"Login attempt by: {username}")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        logging.info("Checking credentials...")
        c.execute("SELECT id, profession FROM users WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()

        if result:
            user_id, profession = result
            logging.info(f"User authenticated. User ID: {user_id}, Profession: {profession}")
            
            # Create session
            session['user_id'] = user_id
            session['profession'] = profession.lower()
            
            if profession.lower() == 'doctor':
                return redirect(url_for('doctor_page'))
            else:
                return jsonify({"success": True, "message": "Login successful, but only doctor accounts have access to a landing page."})
        else:
            logging.warning(f"Invalid credentials for username: {username}")
            return jsonify({"success": False, "message": "Invalid credentials"})
    except sqlite3.Error as e:
        logging.error(f"Database error during login: {e}")
        return jsonify({"success": False, "message": f"Database error: {e}"})
    finally:
        if conn:
            conn.close()

# Route to handle logout
@app.route('/logout')
def logout():
    logging.info(f"Logout request. Session before clearing: {session}")
    session.clear()
    logging.info("Session cleared.")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)