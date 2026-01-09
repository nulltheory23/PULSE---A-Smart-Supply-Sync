from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {"buyers": [], "sellers": []}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

@app.route("/seller/login", methods=["POST"])
def seller_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()["sellers"]

    for u in users:
        if u["username"] == username and u["password"] == password:
            return jsonify({"success": True, "role": "seller"})

    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(debug=True, port=5002)
