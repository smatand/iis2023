from app import app, db

with app.app_context():
    # to check whether the table is created or not
    # enter .tables in sqlite3 terminal
    # 'sqlite3 database.db``
    db.create_all()