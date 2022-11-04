import datetime
from flask import flash, jsonify, redirect, render_template, url_for, Flask, request
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

from db_models import User, db

app = Flask(__name__)

app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(minutes=30)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'  # type: ignore
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(username)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = str(data.get('fullname'))
    username = str(data.get('username'))
    password = str(data.get('password'))
    password_rep = str(data.get('password_rep'))
    try:
        role = int(data.get('role'))
    except:
        role = 1

    error_message = ''

    user = User.query.filter_by(username=username).first()
    if user:
        error_message = "Username already exists!"
    if password != password_rep:
        error_message = "Passwords do not match."
    if not username.startswith('FAC'):
        error_message = "Faculty username should start with 'FAC'."
    if re.findall(r"[^a-zA-Z\d\s:]", full_name+username+password):
        error_message = "Fields cannot contain non-alphanumeric characters."

    db.session.add(User(username=username, password=password, full_name=full_name, role=role))
    db.session.commit()

    if error_message:
        return jsonify({"error_message": error_message})

    return jsonify({"error_message": "success"})

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    username = str(data.get('username'))
    password = str(data.get('password'))

    user = User.query.filter_by(username=username).first()
    if not user or not (user.password == password):
    # TODO: if not user or not check_password_hash(user.password, password):
        return jsonify({"error_message": "Invalid Credentials!"})

    user.authenticated = True
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({"error_message": "success"})

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return "You are logged out!"

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)