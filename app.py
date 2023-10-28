from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin, current_user,
    login_user, LoginManager, login_required, logout_user
)
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.update(
    SECRET_KEY='secret',
    SQLALCHEMY_DATABASE_URI='sqlite:///database.db'
)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=True, unique=True)
    password = db.Column(db.String(25), nullable=False)
    role = db.Column(db.String(25), default='user')

# https://flask-login.readthedocs.org/en/latest/
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/api/ping")
def ping():
    return jsonify({"status": "success"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    user = User.query.filter_by(username=data['username']).first()
    if user:
        return jsonify({'register' : False})

    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({'register' : True})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(username=data['username']).first()
    if user:
        if bcrypt.check_password_hash(user.password, data['password']):
            login_user(user)
            return jsonify({'login' : True})
        else:
            return jsonify({'login' : False, 'message' : 'Incorrect password'})
    
    return jsonify({'login' : False, 'message' : 'User does not exist'})

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'logout' : True, 'user_authenticated' : current_user.is_authenticated}) 

# TODO: delete later
@app.route('/api/protected', methods=['GET'])
@login_required
def protected():
    if current_user.is_authenticated:
        return 'This is a protected page'
    else:
        return 'You are not logged in'