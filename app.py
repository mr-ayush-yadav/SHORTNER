from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# ------------------
# Database Models
# ------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(500))
    short = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------
# Helper Function
# ------------------

def generate_short():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

# ------------------
# Routes
# ------------------

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        short = generate_short()
        new_url = URL(original=request.form['url'], short=short, user_id=current_user.id)
        db.session.add(new_url)
        db.session.commit()
    urls = URL.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', urls=urls)

@app.route('/<short>')
def redirect_url(short):
    url = URL.query.filter_by(short=short).first()
    if url:
        return redirect(url.original)
    return "Not Found"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))from flask import jsonify

@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    data = request.json
    long_url = data.get("url")

    short = generate_short()
    new_url = URL(original=long_url, short=short, user_id=1)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        "short_url": f"https://shortner-qmsc.onrender.com/{short}"
    })