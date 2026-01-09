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
<<<<<<< HEAD
            # 🔴 BEFORE: display_name comparison caused bug
            # ✅ NOW: store username only
            session["logged_hospital"] = username
            return jsonify({"success": True, "redirect": "/dashboard"})
=======
            # Dynamic Redirect based on role
            target_page = "/dashboard" if role == "hospital" else "/seller-dashboard"
            
            if role == "hospital":
                session["logged_hospital"] = u.get("display_name", username)
            
            return jsonify({
                "success": True, 
                "role": role, 
                "redirect": target_page  # <--- THIS IS KEY
            })
>>>>>>> 4cf88a237e7e2a6e5674831981a3a4d24a3f870d

    return jsonify({"success": False}), 401

<<<<<<< HEAD
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
=======
>>>>>>> 4cf88a237e7e2a6e5674831981a3a4d24a3f870d
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

<<<<<<< HEAD
# -------------------------------
# 6. LEDGER (UNCHANGED)
# -------------------------------
@app.route("/ledger")
=======
@app.route("/seller-dashboard")
def seller_dashboard():
    return render_template("seller-dashboard.html")


@app.route("/ledger", methods=["GET"])
>>>>>>> 4cf88a237e7e2a6e5674831981a3a4d24a3f870d
def get_ledger():
    db = get_db()
    txs = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(row) for row in txs])

# -------------------------------
<<<<<<< HEAD
# RUN
=======
# 4. NEW API: Hospital Dashboard Data
# -------------------------------

@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    # If session fails, we'll just show all hospitals for the hackathon demo
    logged_hospital = session.get("logged_hospital", "")

    result = []
    try:
        for h in hospital_data:
            # We skip the hospital that is currently logged in
            if h["Hospital Name"] != logged_hospital:
                inventory = {
                    "Oxygen": h.get("Oxygen Cylinders", 0),
                    "Anesthesia": h.get("Anesthesia Machines", 0),
                    "Sterilizers": h.get("Sterilizers", 0)
                }

                # Handle Blood Supply safely
                blood_data = h.get("Blood Supply", {})
                if isinstance(blood_data, dict):
                    for blood, qty in blood_data.items():
                        inventory[f"Blood {blood}"] = f"{qty} units"

                result.append({
                    "name": h["Hospital Name"],
                    "email": h.get("Email", "N/A"),
                    "phone": h.get("Telephone", "N/A"),
                    "inventory": inventory
                })
        return jsonify(result)
    except Exception as e:
        print(f"Error in /api/hospitals: {e}")
        return jsonify([]) # Return empty list so JS doesn't crash
    

# -------------------------------
# 5. NEW API: Seller Actions
# -------------------------------

@app.route("/api/add-inventory", methods=["POST"])
def add_inventory():
    data = request.json
    item = data.get('item')
    qty = data.get('qty')
    seller_name = "Seller_1" # In a real app, get this from session

    db = get_db()
    # Check if item exists, if so update, else insert
    existing = db.execute("SELECT * FROM inventory WHERE item = ?", (item,)).fetchone()
    
    if existing:
        db.execute("UPDATE inventory SET qty = qty + ? WHERE item = ?", (qty, item))
    else:
        db.execute("INSERT INTO inventory (seller_name, item, qty) VALUES (?, ?, ?)", 
                   (seller_name, item, qty))
    
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Inventory updated!"})

# -------------------------------
# Run App
>>>>>>> 4cf88a237e7e2a6e5674831981a3a4d24a3f870d
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
