import sqlite3
import hashlib
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

# 🔹 IMPORT hospital resource data (used only for network discovery, not inventory)
from hosdata import data as hospital_data

app = Flask(__name__)
CORS(app)

# 🔹 REQUIRED for session handling
app.secret_key = "pulse_secret_key"

# Absolute paths (Render-safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
DATABASE = os.path.join(BASE_DIR, "pulse.db")

# -------------------------------
# 1. Database Setup
# -------------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            seller_name TEXT,
            item TEXT,
            qty INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospital_inventory (
            id INTEGER PRIMARY KEY,
            hospital TEXT,
            item TEXT,
            qty INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            hospital TEXT,
            item TEXT,
            qty INTEGER,
            seller TEXT,
            hash_id TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# Utility Functions
# -------------------------------
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
# 3. Authentication
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role = data.get("role")
    username = data.get("username")
    password = data.get("password")

    users_data = load_users()
    category = "buyers" if role == "hospital" else "sellers"

    for user in users_data.get(category, []):
        if user["username"] == username and user["password"] == password:
            if role == "hospital":
                session["logged_hospital"] = username
                return jsonify({"success": True, "redirect": "/dashboard"})
            else:
                session["logged_seller"] = username
                return jsonify({"success": True, "redirect": "/seller-dashboard"})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# -------------------------------
# 4. API ROUTES
# -------------------------------

# 🔹 Logged-in hospital inventory (LIVE)
@app.route("/api/hospital/me", methods=["GET"])
def get_my_hospital_inventory():
    hospital = session.get("logged_hospital")
    if not hospital:
        return jsonify({"error": "Not logged in"}), 401

    db = get_db()
    rows = db.execute(
        "SELECT item, qty FROM hospital_inventory WHERE hospital = ?",
        (hospital,)
    ).fetchall()
    db.close()

    inventory = {row["item"]: row["qty"] for row in rows}

    return jsonify({
        "name": hospital,
        "inventory": inventory
    })

# 🔹 Seller inventory (LIVE)
@app.route("/api/sellers", methods=["GET"])
def get_sellers():
    db = get_db()
    rows = db.execute("SELECT * FROM inventory").fetchall()
    db.close()
    return jsonify([dict(row) for row in rows])

# 🔹 Network hospital listing (NOT inventory)
@app.route("/api/hospitals", methods=["GET"])
def get_hospitals():
    result = []
    for h in hospital_data:
        inventory = {
            "Oxygen": h.get("Oxygen Cylinders", 0),
            "Anesthesia": h.get("Anesthesia Machines", 0),
            "Sterilizers": h.get("Sterilizers", 0)
        }
        result.append({
            "name": h["Hospital Name"],
            "inventory": inventory
        })
    return jsonify(result)

# -------------------------------
# 5. ORDER TRANSACTION (CORE LOGIC)
# -------------------------------
@app.route("/hospital/request", methods=["POST"])
def hospital_request():
    data = request.get_json()
    hospital = session.get("logged_hospital")
    item = data.get("item", "").strip().capitalize()
    qty = int(data.get("qty", 0))

    if not hospital:
        return jsonify({"status": "Failed", "message": "Not logged in"}), 401

    db = get_db()

    seller = db.execute(
        "SELECT * FROM inventory WHERE item = ? AND qty >= ? LIMIT 1",
        (item, qty)
    ).fetchone()

    if not seller:
        db.close()
        return jsonify({"status": "Pending", "message": "Insufficient stock"})

    tx_hash = hashlib.sha256(
        f"{hospital}{item}{datetime.now()}".encode()
    ).hexdigest()

    # 🔻 Reduce seller stock
    db.execute(
        "UPDATE inventory SET qty = qty - ? WHERE id = ?",
        (qty, seller["id"])
    )

    # 🔺 Increase hospital stock
    existing = db.execute(
        "SELECT * FROM hospital_inventory WHERE hospital = ? AND item = ?",
        (hospital, item)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE hospital_inventory SET qty = qty + ? WHERE hospital = ? AND item = ?",
            (qty, hospital, item)
        )
    else:
        db.execute(
            "INSERT INTO hospital_inventory (hospital, item, qty) VALUES (?, ?, ?)",
            (hospital, item, qty)
        )

    # 🧾 Record transaction
    db.execute(
        "INSERT INTO transactions (hospital, item, qty, seller, hash_id) VALUES (?, ?, ?, ?, ?)",
        (hospital, item, qty, seller["seller_name"], tx_hash)
    )

    db.commit()
    db.close()

    return jsonify({"status": "Matched", "hash": tx_hash})

# -------------------------------
# 6. SELLER ADD INVENTORY
# -------------------------------
@app.route("/api/add-inventory", methods=["POST"])
def add_inventory():
    data = request.json
    item = data.get("item", "").strip().capitalize()
    qty = int(data.get("qty", 0))
    seller = session.get("logged_seller", "seller1")

    db = get_db()
    existing = db.execute(
        "SELECT * FROM inventory WHERE item = ? AND seller_name = ?",
        (item, seller)
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE inventory SET qty = qty + ? WHERE item = ? AND seller_name = ?",
            (qty, item, seller)
        )
    else:
        db.execute(
            "INSERT INTO inventory (seller_name, item, qty) VALUES (?, ?, ?)",
            (seller, item, qty)
        )

    db.commit()
    db.close()
    return jsonify({"success": True})

# -------------------------------
# 7. TRANSACTION LEDGER
# -------------------------------
@app.route("/ledger")
def get_ledger():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM transactions ORDER BY id DESC"
    ).fetchall()
    db.close()
    return jsonify([dict(row) for row in rows])

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
