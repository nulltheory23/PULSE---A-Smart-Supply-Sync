import sqlite3
import hashlib
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

# 🔹 IMPORT hospital resource data
from hosdata import data as hospital_data

app = Flask(__name__)
CORS(app)

# 🔹 REQUIRED for session handling
app.secret_key = "pulse_secret_key"

# Use absolute paths to ensure Render finds files correctly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATABASE = os.path.join(BASE_DIR, 'pulse.db')

# -------------------------------
# 1. Database & User Setup
# -------------------------------
def init_db():
    """Creates the database tables if they don't exist yet."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY, seller_name TEXT, item TEXT, qty INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions 
                      (id INTEGER PRIMARY KEY, hospital TEXT, item TEXT, qty INTEGER, seller TEXT, hash_id TEXT)''')
    conn.commit()
    conn.close()

# Initialize the DB immediately when the app starts
init_db()

def load_users():
    if not os.path.exists(USERS_FILE):
        default_data = {
            "buyers": [{"username": "admin", "password": "123"}], 
            "sellers": [{"username": "seller1", "password": "123"}]
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_data, f)
        return default_data
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# 2. Page Routes
# -------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("hospital-dashboard.html")

@app.route("/login_page")
def show_login():
    return render_template("login.html")

# -------------------------------
# 3. API Routes (EXISTING)
# -------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400
        
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")
    
    users_data = load_users()
    category = "buyers" if role == "hospital" else "sellers"
    users = users_data.get(category, [])

    for u in users:
        if u["username"] == username and u["password"] == password:
            # 🔹 STORE logged-in hospital identity
            if role == "hospital":
                session["logged_hospital"] = u.get("display_name", username)
            return jsonify({"success": True, "role": role, "redirect": "/dashboard"})

    return jsonify({"success": False, "message": "Wrong username or password"}), 401


@app.route("/hospital/request", methods=["POST"])
def hospital_request():
    data = request.get_json()
    hospital = data.get('hospital')
    item = data.get('item')
    qty = data.get('qty')
    
    db = get_db()
    seller = db.execute(
        "SELECT * FROM inventory WHERE item = ? AND qty >= ? LIMIT 1",
        (item, qty)
    ).fetchone()

    if seller:
        tx_hash = hashlib.sha256(f"{hospital}{item}{datetime.now()}".encode()).hexdigest()
        db.execute(
            "INSERT INTO transactions (hospital, item, qty, seller, hash_id) VALUES (?, ?, ?, ?, ?)",
            (hospital, item, qty, seller['seller_name'], tx_hash)
        )
        db.commit()
        db.close()
        return jsonify({"status": "Matched", "match": seller['seller_name'], "hash": tx_hash})
    
    db.close()
    return jsonify({"status": "Pending", "message": "No immediate match found."})


@app.route("/ledger", methods=["GET"])
def get_ledger():
    db = get_db()
    txs = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(row) for row in txs])

# -------------------------------
# 4. NEW API: Hospital Dashboard Data
# -------------------------------

@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    logged_hospital = session.get("logged_hospital")

    result = []

    for h in hospital_data:
        if h["Hospital Name"] != logged_hospital:
            inventory = {
                "Oxygen Cylinders": h["Oxygen Cylinders"],
                "Anesthesia Machines": h["Anesthesia Machines"],
                "Sterilizers": h["Sterilizers"],
                "Surgical Tables": h["Surgical Tables"]
            }

            # Add blood types dynamically
            for blood, qty in h["Blood Supply"].items():
                inventory[f"Blood {blood}"] = f"{qty} units"

            result.append({
                "name": h["Hospital Name"],
                "email": h["Email"],
                "phone": h["Telephone"],
                "inventory": inventory
            })

    return jsonify(result)

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
