from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from yaml import FullLoader, load

from app import bcrypt
from models import (Admission, Category, Event, Place, Review, RoleEnum, User,
                    UserEvent, db)

with open("config.yaml") as f:
    cfg = load(f, Loader=FullLoader)

username = cfg["user"]["name"]
password = cfg["user"]["password"]

ip = cfg["server"]["IP"]
port = cfg["server"]["port"]

database = cfg["database"]["name"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'postgresql://{username}:{password}@{ip}:{port}/{database}'
)

db.init_app(app)

app.app_context().push()

if __name__ == "__main__":
    free_admission = Admission(
            name="free",
            amount=0
            )
    free_admission.insert()

    adult_admission = Admission(
            name="adult",
            amount=100
            )
    adult_admission.insert()

    d105 = Place(
            name="d105",
            address="B/D105",
            description="Room D105"
            )
    d105.insert()

    e112 = Place(
            name="e112",
            address="B/E112",
            description="Room E112"
            )
    e112.insert()

    education = Category(
            name="education",
            description="Education events"
            )
    education.insert()

    lecture = Category(
            name="lecture",
            description="Lecture events",
            parent_id=1
            )
    lecture.insert()

    password = bcrypt.generate_password_hash("user1").decode('utf-8')
    user1 = User(
            name="user1",
            password=password,
            role=RoleEnum.user
            )
    user1.insert()

    password = bcrypt.generate_password_hash("user2").decode('utf-8')
    user2 = User(
            name="user2",
            password=password,
            role=RoleEnum.user
            )
    user2.insert()

    password = bcrypt.generate_password_hash("mod").decode('utf-8')
    mod = User(
            name="mod",
            password=password,
            role=RoleEnum.moderator
            )
    mod.insert()

    password = bcrypt.generate_password_hash("admin").decode('utf-8')
    admin = User(
            name="admin",
            password=password,
            role=RoleEnum.administrator
            )
    admin.insert()

    start = (datetime.now() - timedelta(days=1)).strftime(
            format="%Y-%m-%d %H:%M:%S"
            )
    end = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")
    iis = Event(
            name="IIS",
            start_datetime=start,
            end_datetime=end,
            capacity=150,
            description="IIS lecture",
            image="https://blog.viettelcybersecurity.com/content/images/2022/07/Windows-IIS-1.png",  # noqa
            place_id=1,
            owner_id=1
            )

    iis.admissions.append(adult_admission)
    iis.categories.append(lecture)
    iis.categories.append(education)
    iis.insert()

    isa = Event(
            name="ISA",
            start_datetime=start,
            end_datetime=end,
            capacity=150,
            description="ISA lecture",
            image="https://upload.wikimedia.org/wikipedia/commons/3/36/Isa1.jpg",  # noqa
            place_id=2,
            owner_id=2,
            approved=True
            )

    isa.admissions.append(free_admission)
    isa.categories.append(education)
    isa.insert()

    iis_review = Review(
            comment="best lecture ever",
            rating=10,
            user_id=1,
            event_id=1
            )
    iis_review.insert()

    isa_review = Review(
            comment="it's too long",
            rating=7,
            user_id=2,
            event_id=2
            )
    isa_review.insert()

    user1_iis = UserEvent(
            event_id=1,
            user_id=1
            )
    user2_iis = UserEvent(
            event_id=1,
            user_id=2
            )
    mod_iis = UserEvent(
            event_id=1,
            user_id=3
            )

    user1_iis.insert()
    user2_iis.insert()
    mod_iis.insert()

    user1_isa = UserEvent(
            event_id=2,
            user_id=1
            )
    user2_isa = UserEvent(
            event_id=2,
            user_id=2
            )

    user1_isa.insert()
    user2_isa.insert()

