import os

from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate,identify
from resources.user import UserRegister
from resources.chatbot import Chatbot
from resources.score import Score
from resources.image import Image

upload_folder = '/images'
allowed_extensions = ['png','jpg']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['UPLOAD_FOLDER'] = upload_folder
# do not track through flask SQLAlchemy's tracker, but through SQLAlchemy's
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Martin'
api = Api(app)

# create the database
@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWT(app, authenticate, identify)  # make an endpoint /auth

# routes

api.add_resource(UserRegister,'/register')
api.add_resource(Chatbot, '/chatbot')
api.add_resource(Score, '/score')
api.add_resource(Image, '/image/<string:user_id>/<string:image_id>')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port = 8000, debug=True)