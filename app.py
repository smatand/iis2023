from sqlalchemy.orm import DeclarativeBase
from models import User, RoleEnum, db
from yaml import load, FullLoader
from flask import (
    redirect,
    request,
    Flask,
    render_template,
    url_for
)
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

with open("config.yaml") as f:
    cfg = load(f, Loader=FullLoader)

username = cfg["user"]["name"]
password = cfg["user"]["password"]

ip = cfg["server"]["IP"]
port = cfg["server"]["port"]
database = cfg["database"]["name"]


class Base(DeclarativeBase):
    pass


app = Flask(__name__)

app.config.update(
    SQLALCHEMY_DATABASE_URI=(
        f'postgresql://{username}:{password}@{ip}:{port}/{database}'
    ),
    SECRET_KEY='secret'
)
bcrypt = Bcrypt(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    return render_template('index.html')


@app.route("/home")
@login_required
def home():
    # return current_user.name
    return render_template('home.html', current_user=current_user)


@app.route("/users")
def users():
    user_list = User.get_list()
    print(user_list)
    return str(user_list)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')

        if username is None or password is None:
            return render_template(
                'register.html',
                error="Username or password is empty"
            )

        if db.session.execute(
            db.select(User).filter_by(
                                  name=username
                )).one_or_none() is not None:
            return render_template(
                'register.html',
                error="Username already exists"
            )

        user = User()
        user.name = username
        user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.role = RoleEnum.user
        user.insert()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('name')
        password = request.form.get('password')

        if username is None or password is None:
            return render_template(
                'login.html',
                error="Username or password is empty"
            )

        user = User.query.filter_by(name=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template(
                'login.html',
                error="Username or password is incorrect"
            )

    return render_template('login.html')


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
