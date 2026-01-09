import sqlite3
import hashlib
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = "pulse_secret_key"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "pulse.db")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# -------------------------------
# DATABASE CORE
# -------------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    # 1. Seller Inventory
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        seller_name TEXT,
        item TEXT,
        qty INTEGER
    )""")
    # 2. Private Ledger
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        hospital TEXT,
        item TEXT,
        qty INTEGER,
        seller TEXT,
        hash_id TEXT
    )""")
    # 3. Hospital Profiles
    c.execute("""CREATE TABLE IF NOT EXISTS hospital_profiles (
        id INTEGER PRIMARY KEY,
        hospital TEXT UNIQUE,
        display_name TEXT,
        inventory TEXT
    )""")
    db.commit()
    db.close()
    seed_data()

def seed_data():
    """Initializes marketplace with items from specific sellers."""
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    if count == 0:
        starter_items = [
            ("cms_hospital_ooty", "Oxygen", 100),
            ("nirmala_hospital_kotagiri", "Ventilators", 15),
            ("coonoor_dist_hospital", "Blood_O+", 40),
            ("gpc444", "Surgical_Masks", 500)
        ]
        db.executemany("INSERT INTO inventory (seller_name, item, qty) VALUES (?, ?, ?)", starter_items)
        db.commit()
    db.close()

init_db()

# -------------------------------
# USER MANAGEMENT (Nilgiris Data)
# -------------------------------
def load_users():
    # This matches the JSON structure you provided
    if not os.path.exists(USERS_FILE):
        return {"buyers": [], "sellers": []} 
    with open(USERS_FILE) as f:
        return json.load(f)

# -------------------------------
# AUTHENTICATION
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()
    role, username, password = data["role"], data["username"], data["password"]
    group = "buyers" if role == "hospital" else "sellers"

    for u in users[group]:
        if u["username"] == username and u["password"] == password:
            if role == "hospital":
                session["logged_hospital"] = username
                session["display_name"] = u["display_name"]
                return jsonify({"success": True, "redirect": "/dashboard"})
            else:
                session["logged_seller"] = username
                session["display_name"] = u["display_name"]
                return jsonify({"success": True, "redirect": "/seller-dashboard"})
    return jsonify({"success": False}), 401

# -------------------------------
# PAGES
# -------------------------------
@app.route("/")
def home(): return render_template("index.html")

@app.route("/login_page")
def login_page(): return render_template("login.html")

@app.route("/dashboard")
def dashboard(): return render_template("hospital-dashboard.html")

@app.route("/seller-dashboard")
def seller_dashboard(): return render_template("seller-dashboard.html")

# -------------------------------
# TRACKING SYSTEM (Private)
# -------------------------------
@app.route("/track/<hash_id>")
def track_order(hash_id):
    db = get_db()
    order = db.execute("SELECT * FROM transactions WHERE hash_id=?", (hash_id,)).fetchone()
    db.close()
    
    if not order:
        return "Invalid Tracking Hash", 404
    
    # SECURITY CHECK: Only buyer or seller involved can view
    current_user = session.get("logged_hospital") or session.get("logged_seller")
    if current_user not in [order["hospital"], order["seller"]]:
        return "Access Denied: Unauthorised access to this transaction.", 403

    return render_template("tracking.html", order=order)

# -------------------------------
# APIS
# -------------------------------
@app.route("/api/hospital/profile")
def hospital_profile():
    hospital = session.get("logged_hospital")
    disp_name = session.get("display_name")
    if not hospital: return jsonify({"error": "Unauthorized"}), 401

    db = get_db()
    row = db.execute("SELECT * FROM hospital_profiles WHERE hospital=?", (hospital,)).fetchone()
    if not row:
        default_inv = {"Oxygen": 5, "Masks": 20}
        db.execute("INSERT INTO hospital_profiles VALUES (NULL, ?, ?, ?)",
                   (hospital, disp_name, json.dumps(default_inv)))
        db.commit()
        return jsonify({"display_name": disp_name, "inventory": default_inv})
    
    return jsonify({"display_name": row["display_name"], "inventory": json.loads(row["inventory"])})

@app.route("/api/sellers")
def sellers():
    db = get_db()
    rows = db.execute("SELECT * FROM inventory").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route("/hospital/request", methods=["POST"])
def hospital_request():
    hospital = session.get("logged_hospital")
    data = request.json
    item, qty = data["item"], int(data["qty"])

    db = get_db()
    seller = db.execute("SELECT * FROM inventory WHERE item=? AND qty>=?", (item, qty)).fetchone()

    if not seller:
        db.close()
        return jsonify({"status": "Failed", "message": "Stock unavailable"})

    # 1. Update Inventories
    db.execute("UPDATE inventory SET qty=qty-? WHERE id=?", (qty, seller["id"]))
    
    profile = db.execute("SELECT inventory FROM hospital_profiles WHERE hospital=?", (hospital,)).fetchone()
    if profile:
        inv = json.loads(profile["inventory"])
        inv[item] = inv.get(item, 0) + qty
        db.execute("UPDATE hospital_profiles SET inventory=? WHERE hospital=?", (json.dumps(inv), hospital))

    # 2. Generate Hash & Record (Private Seller User saved)
    tx_hash = hashlib.sha256(f"{hospital}{item}{datetime.now()}".encode()).hexdigest()
    db.execute("INSERT INTO transactions (hospital, item, qty, seller, hash_id) VALUES (?,?,?,?,?)",
               (hospital, item, qty, seller["seller_name"], tx_hash))

    db.commit()
    db.close()
    return jsonify({"status": "Matched", "hash": tx_hash})

@app.route("/ledger")
def ledger():
    """Only shows transactions where the logged user is a participant."""
    h_user = session.get("logged_hospital")
    s_user = session.get("logged_seller")
    db = get_db()
    
    if h_user:
        rows = db.execute("SELECT * FROM transactions WHERE hospital=? ORDER BY id DESC", (h_user,)).fetchall()
    elif s_user:
        rows = db.execute("SELECT * FROM transactions WHERE seller=? ORDER BY id DESC", (s_user,)).fetchall()
    else:
        rows = []
        
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route("/debug/reset")
def reset_db():
    db = get_db()
    db.execute("DELETE FROM inventory"); db.execute("DELETE FROM transactions"); db.execute("DELETE FROM hospital_profiles")
    db.commit(); db.close()
    return "Database Reset."

if __name__ == "__main__":
    app.run(debug=True)