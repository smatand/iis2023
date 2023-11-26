from models import User, RoleEnum, db, Event, Place, Category, Review
from forms import EventForm, PlaceForm, CategoryForm, ReviewForm, FilterForm, EventAttendanceForm, EventAttendanceCancelForm
from yaml import load, FullLoader
from sqlalchemy import and_, or_
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


@app.route("/", methods=['GET', 'POST'])
def index():
    form = FilterForm()
    if form.validate_on_submit():
        name = form.name.data
        category_ids = form.category.data
        place_ids = form.place.data
        approved = form.approved.data

        if approved is False:
            events = Event.query.filter(and_(
                Event.name.ilike('%{}%'.format(name)),
                or_(*[Event.categories.any(
                    id=category_id
                    ) for category_id in category_ids]),
                or_(*[Event.place.has(
                    id=place_id
                    ) for place_id in place_ids]),
            )).all()
        else:
            events = Event.query.filter(and_(
                Event.name.ilike('%{}%'.format(name)),
                or_(Event.approved.is_(True)),
                or_(*[Event.categories.any(
                    id=category_id
                    ) for category_id in category_ids]),
                or_(*[Event.place.has(
                    id=place_id
                    ) for place_id in place_ids])
            )).all()
    else:
        events = Event.query.all()

    month, year = get_month_year()
    month_name = calendar.month_name[month]

    return render_template(
        'index.html',
        form=form,
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
        category_ids = [
            id for id, checked in zip([choice[0] for choice
                                       in form.category_ids.choices
                                       ], form.category_ids.data) if checked]
        place_id = form.place_id.data

        event = Event()
        event.name = form.name.data
        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.capacity = form.capacity.data
        event.description = form.description.data
        event.image = form.image.data
        event.place_id = place_id
        event.owner_id = current_user.id

        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        for category in categories:
            event.categories.append(category)

        if Event.query.filter_by(name=event.name).first():
            flash('Event with the same name already exists')
            return render_template(
                'create_event.html',
                form=form
            )

        db.session.add(event)
        db.session.commit()

        flash(
            'Event has been created. Wait for the approval from moderators',
            'success'
        )
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


@app.route('/event/<int:id>', methods=['GET', 'POST'])
def event(id):
    event = Event.query.get(id)
    now = datetime.now()
    filled_capacity = len(event.users)
    form = ReviewForm()
    attend_form = EventAttendanceForm()
    cancel_attend_form = EventAttendanceCancelForm()

    if request.method == 'POST':

        if form.validate_on_submit() and 'submit_review' in request.form:
            review = Review(
                comment=form.comment.data,
                rating=form.rating.data,
                event_id=id
            )
            review.user_id = current_user.id

            # review could be added only if current_user is in event.users
            if current_user not in event.users:
                flash('You are not a participant of this event')
                return redirect(url_for('event', id=id))

            if Review.query.filter_by(user_id=current_user.id,
                                      event_id=id).first():
                flash('You already have a review for this event')
                return redirect(url_for('event', id=id))

            db.session.add(review)
            db.session.commit()
            return redirect(url_for('event', id=id))
        elif attend_form.validate_on_submit() and 'attend' in request.form:
            if current_user in event.users:
                flash('You are already a participant of this event')
                return redirect(url_for('event', id=id))

            if filled_capacity == event.capacity:
                flash('Sorry, this event is full')
                return redirect(url_for('event', id=id))

            event.users.append(current_user)
            db.session.commit()
            return redirect(url_for('event', id=id))

        elif cancel_attend_form.validate_on_submit() and 'cancel_attend' in request.form:
            if current_user not in event.users:
                flash('You are not a participant of this event')
                return redirect(url_for('event', id=id))

            event.users.remove(current_user)
            db.session.commit()
            return redirect(url_for('event', id=id))

    # don't show unapproved events to users who are not owners
    if not event.approved and event.owner_id != current_user.id:
        flash('You cannot see details of unapproved event, that has not been created by you!')
        return redirect(url_for('index'))

    return render_template('event.html', event=event, now=now, form=form,
                           filled_capacity=filled_capacity,
                           attend_form=attend_form,
                           cancel_attend_form=cancel_attend_form)


@app.route('/propose_place', methods=['GET', 'POST'])
@login_required
def propose_place():
    # prolly smth for moderator? todo
    form = PlaceForm()
    if form.validate_on_submit():
        place = Place()
        place.name = form.name.data
        place.address = form.address.data
        place.description = form.description.data

        if Place.query.filter_by(name=place.name).first():
            flash('Place with the same name already exists')
            return render_template(
                'propose_place.html',
                form=form
            )

        if Place.query.filter_by(address=place.address).first():
            flash('Place with the same address already exists')
            return render_template(
                'propose_place.html',
                form=form
            )

        db.session.add(place)
        db.session.commit()

        flash(
            'Event has been proposed. Wait for the approval from moderators',
            'success'
        )
        return redirect(url_for('places'))

    return render_template('propose_place.html', form=form)


@app.route('/places', methods=['GET'])
@login_required
def places():
    places = Place.query.all()
    events = Event.query.all()
    return render_template('places.html', places=places, events=events)


@app.route('/categories', methods=['GET'])
@login_required
def categories():
    categories = Category.query.all()
    events = Event.query.all()
    return render_template(
        'categories.html',
        categories=categories,
        events=events)


@app.route('/propose_category', methods=['GET', 'POST'])
@login_required
def propose_category():
    form = CategoryForm()
    form.parent_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        category = Category()
        category.name = form.name.data
        category.description = form.description.data
        category.parent_id = form.parent_id.data

        db.session.add(category)
        db.session.commit()

        flash(
            'Category has been proposed, wait for approval',
            'success'
        )
        return redirect(url_for('categories'))

    return render_template('propose_category.html', form=form)
