from flask import Flask
from models import *
from yaml import load, FullLoader

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


@app.route("/")
def hello_world():
    return "<p>Hello world!</p>"


@app.route("/users")
def users():
    user_list = User.get_list()
    print(user_list)
    return str(user_list)
