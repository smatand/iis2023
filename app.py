from models import User, RoleEnum, db, Event
from forms import EventForm
from yaml import load, FullLoader
from flask_bcrypt import Bcrypt
from datetime import datetime
import calendar
from flask import (
    redirect,
    request,
    Flask,
    render_template,
    url_for,
    flash
)
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


def get_month_year():
    year = request.args.get('year', default=datetime.now().year, type=int)
    month = request.args.get('month', default=datetime.now().month, type=int)
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    return month, year


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    events = Event.query.all()

    month, year = get_month_year()
    month_name = calendar.month_name[month]

    return render_template(
        'index.html',
        events=events,
        current_user=current_user,
        calendar=calendar,
        month=month,
        month_name=month_name,
        year=year
    )


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


@app.route("/create_event", methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        event = Event()
        event.name = form.name.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.capacity = form.capacity.data
        event.description = form.description.data
        event.image = form.image.data
        event.place_id = form.place_id.data
        event.users.append(current_user)
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('home'))

    return render_template(
        'create_event.html',
        form=form
    )


@app.route("/home")
@login_required
def home():
    month, year = get_month_year()
    month_name = calendar.month_name[month]

    events = Event.query.filter(Event.users.contains(current_user)).all()

    return render_template(
        'home.html',
        events=events,
        calendar=calendar,
        month=month,
        year=year,
        month_name=month_name
    )


@app.route('/event/<int:id>', methods=['GET'])
def event(id):
    event = Event.get_detail(id)
    return render_template('event.html', event=event)
