from app import app
from db import db

db.init_app(app)
app.run(port = 8000, debug=True)
# create the database
@app.before_first_request
def create_tables():
    db.create_all()