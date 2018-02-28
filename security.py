from models.user import UserModel
from werkzeug.security import safe_str_cmp


def authenticate(user_name,password):
    user = UserModel.find_by_username(user_name)
    # if user and user.password == password:
    if user and safe_str_cmp(user.password,password):
        return user

def identify(payload):
    user_id = payload['identity']
    return UserModel.find_by_id(user_id)
