from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend is live!"

@app.route("/hello")
def hello():
    return {"message": "Hi Vinee, backend is working!"}

if __name__ == "__main__":
    app.run(debug=True)