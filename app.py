import sys
from models import (
    User,
    RoleEnum,
    db,
    Event,
    Place,
    Category,
    Review,
    UserEvent,
    Admission
)
from forms import (
    EventForm,
    PlaceForm,
    CategoryForm,
    ReviewForm,
    FilterForm,
    EventAttendanceForm,
    EventAttendanceCancelForm,
    EventApprovalForm,
    DeleteReviewForm,
    EditEventForm,
    UserSearchForm,
    UserUpdateForm,
    EventApproveRequestForm,
    EventCancelRequestForm
)
from yaml import load, FullLoader
from sqlalchemy import and_, or_
from flask_bcrypt import Bcrypt
from datetime import datetime as dt, timedelta
import calendar
from utils import get_category_choices
from flask import (
    redirect,
    request,
    Flask,
    render_template,
    url_for,
    flash,
    session
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
    year = request.args.get('year', default=dt.now().year, type=int)
    month = request.args.get('month', default=dt.now().month, type=int)
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


# timeout for session
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=10)
    session.modified = True


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


@app.route("/users", methods=['GET', 'POST'])
@login_required
def users():
    if current_user.role.value < RoleEnum.administrator.value:
        return redirect(url_for('index'))

    users = User.query.all()
    form = UserSearchForm()

    if form.validate_on_submit():
        search_term = form.search.data
        users = User.query.filter(User.name == search_term).all()

    return render_template('users.html', form=form, users=users)


@app.route("/edit_user/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role.value < RoleEnum.administrator.value:
        return redirect(url_for('index'))

    user = User.query.get_or_404(id)
    form = UserUpdateForm()

    if form.validate_on_submit():
        desired_role = form.role.data
        user.role = RoleEnum[desired_role].name
        db.session.commit()
        return redirect(url_for('edit_user', id=id))

    return render_template('edit_user.html', form=form, user=user)


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
    form.category_ids.choices = get_category_choices()
    form.category_ids.choices.pop(0)
    if form.validate_on_submit():
        # only get categories that are approved
        category_ids = [
            id for id, checked in zip([choice[0] for choice
                                       in form.category_ids.choices
                                       ], form.category_ids.data) if checked]
        form.category_ids.choices = get_category_choices()

        admission_ids = [
            id for id, checked in zip([choice[0] for choice
                                       in form.admission_ids.choices
                                       ], form.admission_ids.data) if checked]

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

        admissions = Admission.query.filter(
            Admission.id.in_(admission_ids)
            ).all()
        for admission in admissions:
            event.admissions.append(admission)

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
        return redirect(url_for('event', id=event.id))

    return render_template(
        'create_event.html',
        form=form
    )


@app.route("/edit_event/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_event(id):
    event = Event.query.get_or_404(id)
    if event.owner_id != current_user.id:
        flash('This is not your event to edit!')

    if event.approved is True:
        flash('You cannot edit approved events!')
        return redirect(url_for('event', id=id))

    form = EditEventForm()
    form.category_ids.choices = get_category_choices()
    form.category_ids.choices.pop(0)

    if form.validate_on_submit():
        category_ids = [
            id for id, checked in zip([choice[0] for choice
                                       in form.category_ids.choices
                                       ], form.category_ids.data) if checked]
        form.category_ids.choices = get_category_choices()
        admission_ids = [
            id for id, checked in zip([choice[0] for choice
                                      in form.admission_ids.choices], form.admission_ids.data) if checked]

        place_id = form.place_id.data

        event.start_datetime = form.start_datetime.data
        event.end_datetime = form.end_datetime.data
        event.capacity = form.capacity.data
        event.description = form.description.data
        event.image = form.image.data
        event.place_id = place_id

        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        event.categories.clear()
        for category in categories:
            event.categories.append(category)

        admissions = Admission.query.filter(
            Admission.id.in_(admission_ids)
            ).all()
        event.admissions.clear()
        for admission in admissions:
            event.admissions.append(admission)

        if event.approved is True:
            flash('You cannot edit approved event!')
            return redirect(url_for('event', id=id))
        db.session.commit()

        flash('Your event has been updated!', 'success')
        return redirect(url_for('event', id=event.id))

    elif request.method == 'GET':
        form.start_datetime.data = event.start_datetime
        form.end_datetime.data = event.end_datetime
        form.capacity.data = event.capacity
        form.description.data = event.description
        form.image.data = event.image
        form.place_id.data = event.place_id
        form.category_ids.data = [category.id for category in event.categories]
        form.admission_ids.data = [admission.id for admission in event.admissions]

    return render_template('edit_event.html',
                           form=form, event=event)


@app.route("/home")
@login_required
def home():
    month, year = get_month_year()
    month_name = calendar.month_name[month]

    #events = Event.query.filter(Event.users.contains(current_user)).all()
    user_events = UserEvent.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'home.html',
        events=user_events,
        calendar=calendar,
        month=month,
        year=year,
        month_name=month_name
    )


@app.route('/event/<int:id>', methods=['GET', 'POST'])
def event(id):
    event = Event.query.get(id)
    user_events = UserEvent.query.filter_by(event_id=id).all()
    now = dt.now()
    # only events that have user_event.approved = True
    event_users = UserEvent.query.filter_by(
        event_id=id,
        approved=True
    ).all()
    filled_capacity = len(event_users)

    form = ReviewForm()
    attend_form = EventAttendanceForm()
    cancel_attend_form = EventAttendanceCancelForm()
    approval_form = EventApprovalForm()
    request_approval_form = EventApproveRequestForm()
    cancel_request_form = EventCancelRequestForm()

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
            user_event = UserEvent.query.filter_by(
                user_id=current_user.id,
                event_id=id
            ).all()
            if event in user_event:
                flash('You are already a participant of this event')
                return redirect(url_for('event', id=id))

            if filled_capacity == event.capacity:
                flash('Sorry, this event is full')
                return redirect(url_for('event', id=id))

            if event.admissions:
                user_event = UserEvent(
                    user_id=current_user.id,
                    event_id=id,
                    approved=False
                )
                flash('Your request has been sent to the event owner')
            else:
                user_event = UserEvent(
                    user_id=current_user.id,
                    event_id=id
                    # approved is defaultly True
                )

            db.session.add(user_event)
            db.session.commit()
            return redirect(url_for('event', id=id))

        elif request_approval_form.validate_on_submit() \
                and 'approve_request' in request.form:
            user_event = UserEvent.query.filter_by(
                user_id=request.form.get('user_id'),
                event_id=id
            ).first()
            print("User Event Before: ", user_event, file=sys.stderr)

            user_event.approved = True
            db.session.commit()
            return redirect(url_for('event', id=id))

        elif cancel_request_form.validate_on_submit() \
                and 'cancel_request' in request.form:
            user_event = UserEvent.query.filter_by(
                user_id=request.form.get('user_id'),
                event_id=id
            ).first()

            db.session.delete(user_event)
            db.session.commit()
            return redirect(url_for('event', id=id))

        elif attend_form.validate_on_submit() and 'approve' in request.form:
            event.approved = True
            db.session.commit()

        elif cancel_attend_form.validate_on_submit():
            if 'cancel_attend' in request.form:
                user_event = UserEvent.query.filter_by(
                    user_id=current_user.id,
                    event_id=id
                ).first()
                if user_event is None:
                    flash('You are not a participant of this event')
                    return redirect(url_for('event', id=id))

                db.session.delete(user_event)
                db.session.commit()
                return redirect(url_for('event', id=id))

    # don't show unapproved events to users who are not owners
    if (not event.approved and event.owner_id != current_user.id and
            current_user.role.value < RoleEnum.moderator.value):
        flash(
            'You cannot see details of an unapproved event, '
            'that has not been created by you!')
        return redirect(url_for('index'))

    return render_template('event.html', event=event, now=now, form=form,
                           filled_capacity=filled_capacity,
                           attend_form=attend_form,
                           cancel_attend_form=cancel_attend_form,
                           approval_form=approval_form,
                           request_approval_form=request_approval_form,
                           user_events=user_events)


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

        if Place.query.filter(Place.name.like('%' + place.name + '%')).first():
            flash('Place with a similar name already exists')
            return render_template(
                'propose_place.html',
                form=form
            )

        if Place.query.filter(
            Place.address.like('%' + place.address + '%')
                ).first():
            flash('Place with a similar address already exists')
            return render_template(
                'propose_place.html',
                form=form
            )

        db.session.add(place)
        db.session.commit()

        flash(
            'Place has been proposed. Wait for the approval from moderators',
            'success'
        )
        return redirect(url_for('places'))

    return render_template('propose_place.html', form=form)


@app.route('/places', methods=['GET'])
@login_required
def places():
    places = []
    if current_user.role == RoleEnum.moderator or \
            current_user.role == RoleEnum.administrator:
        places = Place.query.all()
    else:
        # user will see only approved places
        places = Place.query.filter_by(approved=True).all()

    events = Event.query.all()
    return render_template('places.html', places=places, events=events)


@app.route('/categories', methods=['GET'])
@login_required
def categories():
    categories = []
    events = Event.query.all()

    if current_user.role == RoleEnum.moderator or \
            current_user.role == RoleEnum.administrator:
        categories = Category.query.all()
    else:
        # user will see only approved categories
        categories = Category.query.filter_by(approved=True).all()

    return render_template(
        'categories.html',
        categories=categories,
        events=events)


@app.route('/propose_category', methods=['GET', 'POST'])
def propose_category():
    form = CategoryForm()
    form.parent_id.choices = get_category_choices()
    if form.validate_on_submit():
        parent_id = int(
            form.parent_id.data
            ) if form.parent_id.data != 'None' else None
        category = Category(
            name=form.name.data,
            description=form.description.data,
            parent_id=parent_id
            )

        if Category.query.filter(
            Category.name.like('%' + category.name + '%'),
                Category.parent_id == category.parent_id).first():
            flash(
                'Category with a similar name already exists under one parent'
            )
            return render_template(
                'propose_category.html',
                form=form
            )

        db.session.add(category)
        db.session.commit()
        flash('Your category proposal has been submitted.')
        return redirect(url_for('index'))
    return render_template('propose_category.html', form=form)


@app.route('/my_reviews', methods=['GET', 'POST'])
@login_required
def my_reviews():
    my_reviews = User.query.get(current_user.id).reviews
    form = DeleteReviewForm()

    if form.validate_on_submit():
        review_id = request.form.get('review_id')
        review = Review.query.get(review_id)
        if review.user_id != current_user.id:
            flash('You can delete only your own reviews')
            return redirect(url_for('home'))

        db.session.delete(review)
        db.session.commit()
        flash('Your review has been deleted!', 'success')
        return redirect(url_for('my_reviews'))

    return render_template(
        'my_reviews.html',
        reviews=my_reviews,
        form=form
    )
