from flask_restful import Resource
from models.message import MessageModel
from flask_jwt import jwt_required
from flask import request
import requests

class Chatbot(Resource):

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

    @classmethod
    def stripString(cls,b_str):
        # remove all of % from android request
        new_str = str()
        ind_str = 0
        while True:
            if b_str[ind_str] == '%':
                # find the next %
                next_pos = b_str.find('%', ind_str + 1)
                if next_pos == -1:
                    # at the end of the string, doesn't have any more %
                    new_str = new_str + b_str[ind_str + 1:]
                    break
                new_str = new_str + b_str[ind_str + 1:next_pos]
                ind_str = next_pos

        return new_str

    @classmethod
    def castToDecimal(cls,h_str):
        d_list = list()
        ind_str = 0
        while ind_str < len(h_str):
            # convert every 2 character in the string into a decimal number
            # and put all of decimal numbers into a list
            temp_str = h_str[ind_str:ind_str + 2]
            d_list.append(int(temp_str, base=16))
            ind_str += 2

        return d_list

    @classmethod
    def castToBytes(cls,d_list):
        # convert the decimal numbers into bytes, every decimal number corresponds to a hexadecimal number
        b_list = list()
        for num in d_list:
            b_list.append(bytes([num]))

        # concantenate bytes into a stream
        b_chars = bytes()
        for b_char in b_list:
            b_chars = b_chars + b_char

        return b_chars

    @classmethod
    def manualDecode(cls,b_str):
        h_str = Chatbot.stripString(b_str)
        d_str = Chatbot.castToDecimal(h_str)
        b_chars = Chatbot.castToBytes(d_str)
        return b_chars.decode(encoding='utf-8')

    @jwt_required()
    def post(self):
        user_id = Chatbot.register_userid()

        data = request.get_json()
        print(data['input_text'])
        #print(type(data['input_text']),type(data['session_id']))
        if data['input_text'].startswith('%'):
            input_text = Chatbot.manualDecode(data['input_text'])
        else:
            input_text = data['input_text']
        [reply_words, e_type, e_score] = Chatbot.get_response(user_id, input_text)
        new_message = MessageModel(data['input_text'],data['session_id'],e_type,e_score)
        new_message.save_to_db()

        return {'response':reply_words,'emotion_type':e_type,'emotion_score':e_score}, 200





