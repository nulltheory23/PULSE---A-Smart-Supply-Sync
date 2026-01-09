import sqlite3
import hashlib
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

from hosdata import data as hospital_data

app = Flask(__name__)
CORS(app)

app.secret_key = "pulse_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATABASE = os.path.join(BASE_DIR, "pulse.db")

# -------------------------------
# 1. Database & User Setup
# -------------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
                      (id INTEGER PRIMARY KEY, seller_name TEXT, item TEXT, qty INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions 
                      (id INTEGER PRIMARY KEY, hospital TEXT, item TEXT, qty INTEGER, seller TEXT, hash_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 🔹 helper (ONLY for fixing comparison bug)
def normalize(text):
    return text.lower().replace(",", "").replace(".", "").replace(" ", "_")

# -------------------------------
# 2. Page Routes
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("hospital-dashboard.html")

@app.route("/login_page")
def show_login():
    return render_template("login.html")

# -------------------------------
# 3. LOGIN (unchanged logic)
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    users_data = load_users()
    users = users_data.get("buyers", [])

    for u in users:
        if u["username"] == username and u["password"] == password:
            # 🔴 BEFORE: display_name comparison caused bug
            # ✅ NOW: store username only
            session["logged_hospital"] = username
            return jsonify({"success": True, "redirect": "/dashboard"})

    return jsonify({"success": False}), 401

# -------------------------------
# 4. DASHBOARD DATA (ONLY BUG FIX HERE)
# -------------------------------
@app.route("/api/hospitals")
def get_hospitals():
    logged_username = session.get("logged_hospital")

    result = []

    for h in hospital_data:
        # 🔹 normalize hospital name ONLY for comparison
        hospital_username = normalize(h["Hospital Name"])

        # 🔹 THIS LINE IS THE FIX
        if hospital_username != logged_username:
            inventory = {
                "Oxygen Cylinders": h["Oxygen Cylinders"],
                "Anesthesia Machines": h["Anesthesia Machines"],
                "Sterilizers": h["Sterilizers"],
                "Surgical Tables": h["Surgical Tables"]
            }

            # 🔹 inventory logic UNCHANGED
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
# 5. EXISTING REQUEST LOGIC (UNCHANGED)
# -------------------------------
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
    return jsonify({"status": "Pending"})

# -------------------------------
# 6. LEDGER (UNCHANGED)
# -------------------------------
@app.route("/ledger")
def get_ledger():
    db = get_db()
    txs = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(row) for row in txs])

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
