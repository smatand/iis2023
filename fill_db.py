from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from models import (
        User, Category, Event, Place, Review, Admission, RoleEnum, UserEvent
)
from yaml import load, FullLoader
from app import bcrypt

with open("config.yaml") as f:
    cfg = load(f, Loader=FullLoader)

username = cfg["user"]["name"]
password = cfg["user"]["password"]

ip = cfg["server"]["IP"]
port = cfg["server"]["port"]

database = cfg["database"]["name"]


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f'postgresql://{username}:{password}@{ip}:{port}/{database}'
)

db.init_app(app)

app.app_context().push()

if __name__ == "__main__":
    incheba = Place(
            name="Incheba expo",
            address="Viedenská cesta 3409/5, 851 01 Petržalka",
            description="multifunkčná hala",
            approved=True
            )

    vodaren = Place(
            name="Vodárenské múzeum",
            address="Devínska cesta 5364, 841 04 Karlova Ves",
            description="múzeum vodárenstva",
            approved=True
            )

    hala = Place(
            name="ARENA BRNO",
            address="603 00 Brno-střed, Česko",
            description="plánovaná multifunkční hala",
            approved=False
            )
    vystaviste = Place(
            name="Brněnské výstaviště",
            address="603 00 Brno-Pisárky, Česko",
            description="český výstavní areál",
            approved=True
            )
    d105 = Place(
                name="D105",
                address="Kolejní 2, 612 00 Brno-Královo Pole, Česko",
                description="posluchárna",
                approved=True
    )

    db.session.add(incheba)
    db.session.add(vodaren)
    db.session.add(hala)
    db.session.add(vystaviste)
    db.session.add(d105)
    db.session.commit()

    sport = Category(
            name="šport",
            description="športové aktivity",
            approved=True
            )

    hokej = Category(
                name="hokej",
                description="hokejové zápasy",
                parent_id=1,
                approved=False
                )
    futbal = Category(
                name="futbal",
                description="futbalové zápasy",
                parent_id=1,
                approved=True
                )
    tenis = Category(
                name="tenis",
                description="tenisové zápasy",
                parent_id=1,
                approved=True
                )
    hudba = Category(
                name="hudba",
                description="hudobné podujatia",
                approved=True
                )
    symfonia = Category(
                name="symfónia",
                description="symfonické koncerty",
                parent_id=5,
                approved=True
                )
    rock = Category(
                name="rock",
                description="rockové koncerty",
                parent_id=5,
                approved=True
                )
    education = Category(
                name="vzdelanie",
                description="vzdelávacie aktivity",
                approved=True
                )

    lecture = Category(
            name="prednáška",
            parent_id=8,
            approved=True
    )

    online = Category(
                name="online",
                description="prostredníctvom PC",
                parent_id=9,
                approved=True

                )
    offline = Category(
                name="offline",
                description="v reálnom priestore",
                parent_id=9,
                approved=True
                )

    db.session.add(sport)
    db.session.add(hokej)
    db.session.add(futbal)
    db.session.add(tenis)
    db.session.add(hudba)
    db.session.add(symfonia)
    db.session.add(rock)
    db.session.add(education)
    db.session.add(lecture)
    db.session.add(online)
    db.session.add(offline)
    db.session.commit()

    student_admission = Admission(
            name="študent",
            amount=10
    )
    adult_admission = Admission(
                name="dospelý",
                amount=20
        )
    db.session.add(student_admission)
    db.session.add(adult_admission)
    db.session.commit()

    user1 = User(
            name="tester",
            password=bcrypt.generate_password_hash("Tester123*").decode(
                    'utf-8'
                    ),
            role=RoleEnum.user
            )

    user2 = User(
            name="popocatepepl",
            password=bcrypt.generate_password_hash("Tester123*").decode(
                    'utf-8'
                        ),
            role=RoleEnum.user
            )
    user3 = User(
                name="hraskovie",
                password=bcrypt.generate_password_hash("Tester123*").decode(
                        'utf-8'
                        ),
                role=RoleEnum.user
    )

    mod = User(
            name="moderator",
            password=bcrypt.generate_password_hash("modTester123*").decode(
                    'utf-8'
                    ),
            role=RoleEnum.moderator
            )
    admin = User(
            name="admin",
            password=bcrypt.generate_password_hash("adminTester123*").decode(
                    'utf-8'
                    ),
            role=RoleEnum.administrator
            )

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(mod)
    db.session.add(admin)
    db.session.commit()

    futbal_zapas = Event(
            name="Real Madrid - Barcelona",
            start_datetime="2023-11-01 20:00:00",
            end_datetime="2023-11-01 22:00:00",
            place=vystaviste,
            capacity=500,
            description="El klasico",
            image="https://www.fczbrno.cz/img/luzanky-clanek.png",
            owner_id=1,
            approved=True,
    )
    futbal_zapas.categories.append(sport)
    futbal_zapas.categories.append(futbal)

    koncert = Event(
                name="Hans Zimmer Bratislava",
                start_datetime="2023-11-30 19:00:00",
                end_datetime="2023-11-30 22:00:00",
                place=incheba,
                capacity=1200,
                description="Koncert slávneho skladateľa",
                image="""https://www.billboard.com/wp-content/uploads/2021/"""
                """11/hans-zimmer-oscar-music-billboard-sound-bb16-1548.jpg""",
                owner_id=2,
                approved=True,
        )
    koncert2 = Event(
                name="Hans Zimmer Brno",
                start_datetime="2023-12-13 18:00:00",
                end_datetime="2023-12-13 21:00:00",
                place=vystaviste,
                capacity=1000,
                description="Koncert slávneho skladateľa",
                image="""https://www.billboard.com/wp-content/uploads/2021/"""
                """11/hans-zimmer-oscar-music-billboard-sound-bb16-1548.jpg""",
                owner_id=2,
                approved=True,
        )
    koncert3 = Event(
                name="Iron Maiden",
                start_datetime="2023-12-18 18:00:00",
                end_datetime="2023-12-18 23:59:59",
                place=vodaren,
                capacity=1000,
                description="Koncert slávnej skupiny",
                image="""https://i.scdn.co/image"""
                """/ab67616100005174232a905537f61c00da9d16e0""",
                owner_id=1,
                approved=False,  # append rock to categories
        )
    iis = Event(
            name="IIS prednáška 1",
            start_datetime="2023-11-30 18:00:00",
            end_datetime="2023-11-30 20:00:00",
            place=d105,
            capacity=1,
            description="IIS prednáška",
            owner_id=3,
            approved=True
    )
    koncert.categories.append(hudba)
    koncert.categories.append(symfonia)
    koncert2.categories.append(hudba)
    koncert2.categories.append(symfonia)
    koncert3.categories.append(hudba)
    iis.categories.append(education)
    iis.categories.append(lecture)
    iis.categories.append(offline)

    koncert2.admissions.append(student_admission)
    koncert2.admissions.append(adult_admission)

    db.session.add(futbal_zapas)
    db.session.add(koncert)
    db.session.add(koncert2)
    db.session.add(koncert3)
    db.session.add(iis)
    db.session.commit()

    user_event = UserEvent(
        event_id=2,
        user_id=1,
    )
    db.session.add(UserEvent(
        event_id=2,
        user_id=1,
    ))
    db.session.add(UserEvent(
        event_id=2,
        user_id=2,
    ))
    db.session.add(UserEvent(
        event_id=2,
        user_id=3,
    ))
    db.session.add(UserEvent(
        event_id=2,
        user_id=4,
    ))
    db.session.add(UserEvent(
        event_id=3,
        user_id=4,
    ))
    db.session.add(UserEvent(
        event_id=3,
        user_id=3,
    ))
    db.session.add(UserEvent(
        event_id=3,
        user_id=2,
    ))
    db.session.add(UserEvent(
        event_id=3,
        user_id=1,
    ))
    db.session.add(UserEvent(
        event_id=5,
        user_id=1,
    ))
    db.session.commit()

    futbal_zapas = Review(
            comment="hrozne dobrý zápas, bavili ma fanúšikovia",
            rating=10,
            user_id=1,
            event_id=1
    )
    db.session.add(futbal_zapas)
    db.session.commit()
