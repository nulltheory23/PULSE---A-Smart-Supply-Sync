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

# Use absolute paths for Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATABASE = os.path.join(BASE_DIR, 'pulse.db')

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

@app.route("/seller-dashboard")
def seller_dashboard():
    return render_template("seller-dashboard.html")

@app.route("/login_page")
def show_login():
    return render_template("login.html")

# -------------------------------
# 3. API Routes
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")
    
    users_data = load_users()
    category = "buyers" if role == "hospital" else "sellers"
    users = users_data.get(category, [])

    for u in users:
        if u["username"] == username and u["password"] == password:
            target_page = "/dashboard" if role == "hospital" else "/seller-dashboard"
            
            if role == "hospital":
                session["logged_hospital"] = username
            else:
                session["logged_seller"] = username
            
            return jsonify({"success": True, "role": role, "redirect": target_page})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    logged_username = session.get("logged_hospital", "")
    result = []
    
    try:
        for h in hospital_data:
            hospital_username = normalize(h["Hospital Name"])
            # Skip the hospital currently logged in
            if hospital_username != logged_username:
                inventory = {
                    "Oxygen": h.get("Oxygen Cylinders", 0),
                    "Anesthesia": h.get("Anesthesia Machines", 0),
                    "Sterilizers": h.get("Sterilizers", 0)
                }
                blood_data = h.get("Blood Supply", {})
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
        return jsonify([])

@app.route("/hospital/request", methods=["POST"])
def hospital_request():
    data = request.get_json()
    hospital = data.get('hospital')
    item = data.get('item', '').strip().capitalize()
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

@app.route("/api/add-inventory", methods=["POST"])
def add_inventory():
    data = request.json
    item = data.get('item', '').strip().capitalize()
    qty = data.get('qty')
    seller_name = session.get("logged_seller", "Seller_1")

    db = get_db()
    existing = db.execute("SELECT * FROM inventory WHERE item = ?", (item,)).fetchone()
    if existing:
        db.execute("UPDATE inventory SET qty = qty + ? WHERE item = ?", (qty, item))
    else:
        db.execute("INSERT INTO inventory (seller_name, item, qty) VALUES (?, ?, ?)", 
                   (seller_name, item, qty))
    db.commit()
    db.close()
    return jsonify({"success": True, "message": "Inventory updated!"})

@app.route("/ledger")
def get_ledger():
    db = get_db()
    txs = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(row) for row in txs])

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)