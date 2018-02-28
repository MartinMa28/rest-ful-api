from flask_restful import Resource,reqparse
from models.message import MessageModel
from flask_jwt import jwt_required
import requests

class Chatbot(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('input_text',
                        type=str,
                        required=True,
                        help='This field cannot be left black'
                        )
    parser.add_argument('session_id',
                        type=int,
                        required=True,
                        help='every message should have a session id')
    appID = "5a200ce8e6ec3a6506030e54ac3b970e"

    @classmethod
    def register_userid(cls):

        register_data = {"cmd": "register", "appid": cls.appID}
        url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
        r = requests.post(url, params=register_data)
        jsondata = r.json()

        # Grab the part called data from the response, response_data is a list that has only one item in it.
        response_data = jsondata['data']
        user_id = response_data[0].get('value')
        return user_id

    @classmethod
    def get_response(cls,user_id,input_text):
        chat_data = {
            'cmd': 'chat',
            'appid': cls.appID,
            'userid': user_id,
            'text': input_text,
            'location': ''
        }

        url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
        res_chat = requests.post(url, params=chat_data)
        res_chat_jsondata = res_chat.json()  # The response in json format
        if res_chat_jsondata['return'] != 0:  # Return doesn't equal 0 means going wrong
            return 'going wrong'

        try:
            reply_data = res_chat_jsondata['data']
            reply_words = reply_data[0].get('value')
        except:
            return 'no reply'

        emotion_data = res_chat_jsondata['emotion']
        emotion_type = emotion_data[0].get('value')
        emotion_score = emotion_data[0].get('score')
        emotion_score = float(emotion_score)

        return [reply_words,emotion_type,emotion_score]

    @jwt_required()
    def post(self):
        user_id = Chatbot.register_userid()
        request_data = Chatbot.parser.parse_args()
        [reply_words, e_type, e_score] = Chatbot.get_response(user_id, request_data['input_text'])
        new_message = MessageModel(request_data['input_text'],request_data['session_id'],e_type,e_score)
        new_message.save_to_db()

        return {'response':reply_words,'emotion_type':e_type,'emotion_score':e_score}, 200




