from models import *
from app import *
from datetime import datetime, timedelta

with open("config.yaml") as f:
    cfg = load(f, Loader=FullLoader)

username = cfg["user"]["name"]
password = cfg["user"]["password"]

ip = cfg["server"]["IP"]
port = cfg["server"]["port"]

database = cfg["database"]["name"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f'postgresql://{username}:{password}@{ip}:{port}/{database}'
db.init_app(app)

app.app_context().push()

if __name__ == "__main__":
    d105 = Place(name="d105", address="B/D105", description="Room D105")
    e112 = Place(name="e112", address="B/E112", description="Room E112")

    education = Category(name="education", description="Education events")
    db.session.add(education)
    db.session.commit()
    
    lecture = Category(name="lecture", description="Lecture events", parent_id=1)

    user1 = User(name="user1", password="user1", role=RoleEnum.user)
    user2 = User(name="user2", password="user2", role=RoleEnum.user)
    mod = User(name="mod", password="mod", role=RoleEnum.moderator)
    admin = User(name="admon", password="admin", role=RoleEnum.administrator)
    
    start = datetime.today()
    end = start + timedelta(hours=+2)
    iis = Event(name="IIS", start_datetime=start, end_datetime=end, capacity=150, description="IIS lecture", image="https://blog.viettelcybersecurity.com/content/images/2022/07/Windows-IIS-1.png", place_id=1)
    isa = Event(name="ISA", start_datetime=start, end_datetime=end, capacity=150, description="ISA lecture", image="https://upload.wikimedia.org/wikipedia/commons/3/36/Isa1.jpg", place_id=2)
    
    iis_review = Review(comment="best lecture ever", rating=10, user_id=1, event_id=1)
    isa_review = Review(comment="it's too long", rating=7, user_id=2, event_id=2)

    free_admission = Admission(name="free", amount=0)

    iis.categories.append(lecture)
    iis.categories.append(education)
    isa.categories.append(education)

    iis.users.append(user1)
    iis.users.append(user2)
    iis.users.append(mod)
    isa.users.append(user1)
    isa.users.append(user2)

    isa.admissions.append(free_admission)

    db.session.add(d105)
    db.session.add(e112)
    db.session.commit()
    db.session.add(education)
    db.session.commit()
    db.session.add(lecture)
    db.session.commit()
    db.session.add(user1)
    db.session.commit()
    db.session.add(user2)
    db.session.commit()
    db.session.add(mod)
    db.session.commit()
    db.session.add(admin)
    db.session.commit()
    db.session.add(iis)
    db.session.commit()
    db.session.add(isa)
    db.session.commit()
    db.session.add(iis_review)
    db.session.commit()
    db.session.add(isa_review)
    db.session.commit()
    db.session.add(free_admission)
    db.session.commit()
