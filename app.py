from flask import Flask, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import string
import random
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -----------------------
# DATABASE MODELS
# -----------------------

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500))
    short = db.Column(db.String(10), unique=True)

# -----------------------
# CREATE DATABASE
# -----------------------

with app.app_context():
    db.create_all()

# -----------------------
# HELPER FUNCTION
# -----------------------

def generate_short():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# -----------------------
# ROUTES
# -----------------------

@app.route("/")
def home():
    return "Shortner is Running 🚀"

@app.route("/<short>")
def redirect_url(short):
    link = URL.query.filter_by(short=short).first()
    if link:
        return redirect(link.original)
    return "Link Not Found ❌"

@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "No URL provided"}), 400

    long_url = data["url"]

    short = generate_short()
    while URL.query.filter_by(short=short).first():
        short = generate_short()

    new_url = URL(original=long_url, short=short)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        "short_url": f"https://shortner-qmsc.onrender.com/{short}"
    })