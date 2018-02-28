from flask_restful import Resource,reqparse
from models.user import UserModel


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type = str,
                        required = True,
                        help = 'username is needed')
    parser.add_argument('password',
                        type = str,
                        required = True,
                        help = 'password is needed')
    # create a user
    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'A user with that username already exists'}, 400

        new_user = UserModel(**data)
        new_user.save_to_db()

        return {'message': 'user is created successfully'}, 201




