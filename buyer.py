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

@app.route("/buyer/login", methods=["POST"])
def buyer_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()["buyers"]

    for u in users:
        if u["username"] == username and u["password"] == password:
            return jsonify({"success": True, "role": "buyer"})

    return jsonify({"success": False})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
