from flask import Flask, render_template, request, redirect, jsonify, url_for
import sqlite3
import os
@app.route('/appointments')
def appointments_page():
    return render_template('appointments.html')
app = Flask(__name__)

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
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
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

# Route to render the doctor page
@app.route('/doctor')
def doctor_page():
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

        print(f"Received signup data: {name}, {username}, {address}, {profession}")

        # Validate username format
        if "@" not in username:
            print("Invalid username format.")
            return jsonify({"success": False, "message": "Invalid username format"})

        # Insert data into the users table
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        print("Inserting user into database...")
        c.execute("INSERT INTO users (name, username, password, address, profession) VALUES (?, ?, ?, ?, ?)",
                  (name, username, password, address, profession))

        conn.commit()
        print("User added successfully.")
        return redirect(url_for('login_page'))

    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        return jsonify({"success": False, "message": f"Username already taken: {e}"})
    except sqlite3.Error as e:
        print(f"Database error during signup: {e}")
        return jsonify({"success": False, "message": f"Database error: {e}"})
    finally:
        if conn:
            conn.close()

# Route to handle the login form submission asynchronously
@app.route('/login', methods=['POST'])
async def login_user():
    try:
        username = request.form['username']
        password = request.form['password']

        print(f"Login attempt by: {username}")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        print("Checking credentials...")
        c.execute("SELECT profession FROM users WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()

        if result:
            profession = result[0].lower()
            print(f"Profession found: {profession}")
            if profession == 'doctor':
                return redirect(url_for('doctor_page'))
            else:
                return jsonify({"success": True, "profession": profession})
        else:
            print("Invalid credentials.")
            return jsonify({"success": False, "message": "Invalid credentials"})
    except sqlite3.Error as e:
        print(f"Database error during login: {e}")
        return jsonify({"success": False, "message": f"Database error: {e}"})
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
