from flask import Flask, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import string
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db"
)

db = SQLAlchemy(app)

# -----------------------
# DATABASE MODELS
# -----------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500))
    short = db.Column(db.String(50), unique=True)
    clicks = db.Column(db.Integer, default=0)

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
    return render_template("index.html")

@app.route("/<short>")
def redirect_url(short):
    link = URL.query.filter_by(short=short).first()
    if link:
        link.clicks += 1
        db.session.commit()
        return redirect(link.original)
    return "Link Not Found ❌"

@app.route("/stats/<short>")
def stats(short):
    link = URL.query.filter_by(short=short).first()
    if link:
        return f"Clicks: {link.clicks}"
    return "Not Found"

@app.route("/api/shorten", methods=["POST"])
def api_shorten():

    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    data = request.get_json()

    if not data or "url" not in data:
        return jsonify({"error": "No URL provided"}), 400

    long_url = data["url"]
    custom_short = data.get("custom")

    if custom_short:
        if URL.query.filter_by(short=custom_short).first():
            return jsonify({"error": "Custom URL already taken"}), 400
        short = custom_short
    else:
        short = generate_short()
        while URL.query.filter_by(short=short).first():
            short = generate_short()

    new_url = URL(
        original=long_url,
        short=short,
        user_id=session["user_id"]
    )

    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        "short_url": f"http://127.0.0.1:5000/{short}"
    })


    return jsonify({
        "short_url": f"https://shortner-qmsc.onrender.com/{short}"
    })

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id

    return jsonify({"message": "Login successful"})

    @app.route("/login-page")
    def login_page():
        return '''
        <form action="/login-browser" method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Login</button>
        </form>
        '''

@app.route("/login-browser", methods=["POST"])
def login_browser():
    username = request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return "Invalid credentials"

    session["user_id"] = user.id
    return "Login successful! Go to /dashboard"   

    @app.route("/dashboard")
    def dashboard():

        if "user_id" not in session:
            return "Login required"

        user_links = URL.query.filter_by(user_id=session["user_id"]).all()

        if not user_links:
            return "No links created yet"

        result = ""
    for link in user_links:
        result += f"""
        Short: {link.short} <br>
        Original: {link.original} <br>
        Clicks: {link.clicks} <br><br>
        """

    return result

if __name__ == "__main__":
    app.run(debug=True)