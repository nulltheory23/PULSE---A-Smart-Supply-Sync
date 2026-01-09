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
DATABASE = os.path.join(BASE_DIR, "pulse.db")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# -------------------------------
# DATABASE
# -------------------------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        seller_name TEXT,
        item TEXT,
        qty INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        hospital TEXT,
        item TEXT,
        qty INTEGER,
        seller TEXT,
        hash_id TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS hospital_profiles (
        id INTEGER PRIMARY KEY,
        hospital TEXT UNIQUE,
        display_name TEXT,
        inventory TEXT
    )""")

    db.commit()
    db.close()

init_db()

# -------------------------------
# USERS
# -------------------------------
def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({
                "buyers": [{"username": "admin", "password": "123"}],
                "sellers": [{"username": "seller1", "password": "123"}]
            }, f)
    with open(USERS_FILE) as f:
        return json.load(f)

# -------------------------------
# PAGES (⚠️ LOGIN FIX HERE)
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login_page")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("hospital-dashboard.html")

@app.route("/seller-dashboard")
def seller_dashboard():
    return render_template("seller-dashboard.html")

# -------------------------------
# LOGIN
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()

    role = data["role"]
    username = data["username"]
    password = data["password"]

    group = "buyers" if role == "hospital" else "sellers"

    for u in users[group]:
        if u["username"] == username and u["password"] == password:
            if role == "hospital":
                session["logged_hospital"] = username
                return jsonify({"success": True, "redirect": "/dashboard"})
            else:
                session["logged_seller"] = username
                return jsonify({"success": True, "redirect": "/seller-dashboard"})

    return jsonify({"success": False}), 401

# -------------------------------
# HOSPITAL PROFILE
# -------------------------------
@app.route("/api/hospital/profile", methods=["GET", "POST"])
def hospital_profile():
    hospital = session.get("logged_hospital")
    if not hospital:
        return jsonify({"error": "Not logged in"}), 401

    db = get_db()

    if request.method == "GET":
        row = db.execute(
            "SELECT * FROM hospital_profiles WHERE hospital=?",
            (hospital,)
        ).fetchone()

        if not row:
            default_inventory = {"Oxygen": 10, "Masks": 50}
            db.execute(
                "INSERT INTO hospital_profiles VALUES (NULL, ?, ?, ?)",
                (hospital, hospital.capitalize(), json.dumps(default_inventory))
            )
            db.commit()
            return jsonify({
                "display_name": hospital.capitalize(),
                "inventory": default_inventory
            })

        return jsonify({
            "display_name": row["display_name"],
            "inventory": json.loads(row["inventory"])
        })

    data = request.json
    db.execute(
        "UPDATE hospital_profiles SET display_name=?, inventory=? WHERE hospital=?",
        (data["display_name"], json.dumps(data["inventory"]), hospital)
    )
    db.commit()
    return jsonify({"success": True})

# -------------------------------
# OTHER HOSPITALS
# -------------------------------
@app.route("/api/hospitals/others")
def other_hospitals():
    db = get_db()
    rows = db.execute(
        "SELECT display_name, inventory FROM hospital_profiles"
    ).fetchall()
    db.close()

    return jsonify([
        {"name": r["display_name"], "inventory": json.loads(r["inventory"])}
        for r in rows
    ])

# -------------------------------
# SELLERS
# -------------------------------
@app.route("/api/sellers")
def sellers():
    db = get_db()
    rows = db.execute("SELECT * FROM inventory").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/add-inventory", methods=["POST"])
def add_inventory():
    seller = session.get("logged_seller")
    data = request.json

    db = get_db()
    existing = db.execute(
        "SELECT * FROM inventory WHERE seller_name=? AND item=?",
        (seller, data["item"])
    ).fetchone()

    if existing:
        db.execute(
            "UPDATE inventory SET qty=qty+? WHERE id=?",
            (data["qty"], existing["id"])
        )
    else:
        db.execute(
            "INSERT INTO inventory VALUES (NULL,?,?,?)",
            (seller, data["item"], data["qty"])
        )

    db.commit()
    return jsonify({"success": True})

# -------------------------------
# ORDERS
# -------------------------------
@app.route("/hospital/request", methods=["POST"])
def hospital_request():
    hospital = session.get("logged_hospital")
    data = request.json
    item, qty = data["item"], int(data["qty"])

    db = get_db()
    seller = db.execute(
        "SELECT * FROM inventory WHERE item=? AND qty>=?",
        (item, qty)
    ).fetchone()

    if not seller:
        return jsonify({"status": "Failed"})

    db.execute(
        "UPDATE inventory SET qty=qty-? WHERE id=?",
        (qty, seller["id"])
    )

    tx_hash = hashlib.sha256(
        f"{hospital}{item}{datetime.now()}".encode()
    ).hexdigest()

    db.execute(
        "INSERT INTO transactions VALUES (NULL,?,?,?,?,?)",
        (hospital, item, qty, seller["seller_name"], tx_hash)
    )

    db.commit()
    return jsonify({"status": "Matched", "hash": tx_hash})

@app.route("/ledger")
def ledger():
    db = get_db()
    rows = db.execute("SELECT * FROM transactions ORDER BY id DESC").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])
