from flask_restful import Resource
from models.user import UserModel
from flask import request


class UserRegister(Resource):

    # create a user
    def post(self):
        #data = UserRegister.parser.parse_args()
        data = request.get_json()
        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        new_user = UserModel(data['username'],data['password'])
        new_user.save_to_db()

        return {'message': 'user is created successfully'}, 201




