# -*- coding: utf-8 -*-
from flask_restful import reqparse,Resource
from flask_jwt import jwt_required
from models.message import MessageModel
import numpy as np
import requests
import json


class Score(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('session_id',
                        type=int,
                        required=True,
                        help='every message should have a session id')
    app_id = "5a200ce8e6ec3a6506030e54ac3b970e"

    @jwt_required()
    def post(self):
        request_data = Score.parser.parse_args()
        messages = MessageModel.get_messages_by_session_id(request_data['session_id'])

        user_id = Score.register_userid()
        print(user_id.encode(encoding = 'utf-8'))
        [d_total_result, d_length_result] = Score.parse_txt(messages,user_id)

        d_analyzed_result = Score.analyze_txt(d_total_result, d_length_result)
        v_std = np.load('v_std27.npy')
        v_diary = Score.vectorize(d_analyzed_result)
        final_result = Score.grade(v_diary, v_std)

        emotion_score = np.sum(final_result, axis=1).ravel()
        return {'score':emotion_score[0]}

    @classmethod
    def init_emotions_dict(cls):
        emotions_handle = open('emotions.txt', 'r',encoding='utf-8')
        emotions_dict = dict()
        emotion_ID = 0
        # generate emotion dictionary
        for line in emotions_handle:
            emotion = line.rstrip()
            emotions_dict[emotion] = emotion_ID
            emotion_ID += 1
        return emotions_dict

    @classmethod
    def register_userid(cls):

        register_data = {"cmd": "register", "appid": cls.app_id}
        url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
        r = requests.post(url, params=register_data)
        #jsondata = r.json()
        response = json.dumps(r.json(), ensure_ascii=False)
        jsondata = json.loads(response)

        # Grab the part called data from the response, response_data is a list that has only one item in it.
        response_data = jsondata['data']
        user_id = response_data[0].get('value')
        return user_id

    @classmethod
    def parse_txt(cls,handle,user_id):
        total_result = list()
        note_result = list()
        length_result = list()  # store how many kinds of emotion within every note
        emotion_counter = 0
        for line in handle:
            if line.value.startswith('*'):  # The symbol of the end of that note
                total_result.append(note_result)
                note_result = list()
                length_result.append(emotion_counter)
                emotion_counter = 0
                continue

            chat_data = {
                'cmd': 'chat',
                'appid': cls.app_id,
                'userid': user_id,
                'text': line,
                'location': ''
            }

            # url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
            # res_chat = requests.post(url, params=chat_data)
            # res_chat_jsondata = res_chat.json()  # The response in json format
            # if res_chat_jsondata['return'] != 0:  # Return doesn't equal 0 means going wrong
            #     print(res_chat_jsondata['return_message'])

            # Get the emotion info and print it
            #emotion_data = res_chat_jsondata['emotion']
            emotion_type = line.emotion_type
            emotion_score = line.emotion_score
            emotion_score = float(emotion_score)

            note_result.append({'Type': emotion_type, 'Score': emotion_score})
            emotion_counter += 1

        total_result.append(note_result)
        length_result.append(emotion_counter)
        return [total_result, length_result]

    @classmethod
    def analyze_txt(cls, total_result, length_result):
        analyzed_result = list()
        for note_index in range(0, len(total_result)):
            # the result of every note, keys in it refer to various types of moods
            single_result = dict()  # {'mood_type1': [times,cum_score]}
            for words in total_result[note_index]:
                if words['Type'] in single_result:
                    single_result[words['Type']][0] += 1
                    single_result[words['Type']][1] += words['Score']
                else:
                    single_result[words['Type']] = [1, words['Score']]
            avg_result = list()
            for key, value in list(single_result.items()):
                avg_score = value[1] / value[0]  # value[0] stands for times, value[1] stands for cum_score
                emotion_proportion = value[0] / length_result[note_index]
                avg_result.append((key, value[0], emotion_proportion, avg_score))

            analyzed_result.append(avg_result)
        return analyzed_result

    @classmethod
    def vectorize(cls, r):
        v_result = np.zeros((len(r), 27))  # 27 kinds of emotion, each kind 1 bit
        note_index = 0
        emotions_dict = Score.init_emotions_dict()
        for note in r:
            for emotion in note:
                if emotion[3] > 59 and emotion[0] != '中性':
                    e_label = emotions_dict[emotion[0]]
                    e_vector = np.zeros((1, 27))
                    e_vector[0, e_label] = (1 + emotion[1] / 10) * emotion[2] * emotion[3] / 100
                    v_result[note_index] = v_result[note_index] + e_vector
            note_index += 1
        return v_result

    @classmethod
    def grade(cls, r, std):
        final_result = np.zeros((len(r), 27))
        sentence_index = 0
        for sentence in r:
            question_index = 0
            for question in std:
                score = sentence[question > 0] / question[question > 0]
                score = np.mean(score)
                if score > 1.0:
                    final_result[sentence_index, question_index] = 3
                elif score > 0.6:
                    final_result[sentence_index, question_index] = 2
                elif score > 0.3:
                    final_result[sentence_index, question_index] = 1
                question_index += 1
            sentence_index += 1
        return final_result