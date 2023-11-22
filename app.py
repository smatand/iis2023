from flask import Flask
from models import *


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://admin:changeme@localhost/database"
db.init_app(app)


@app.route("/")
def hello_world():
    return "<p>Hello world!</p>"
