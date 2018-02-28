import requests
import numpy as np
import json

emotions_handle = open('emotions.txt','r')
emotions_dict = dict()
emotion_ID = 0
# generate emotion dictionary
for line in emotions_handle:
    emotion = line.rstrip()
    emotions_dict[emotion] = emotion_ID
    emotion_ID += 1

appID = "5a200ce8e6ec3a6506030e54ac3b970e"
register_data = {"cmd": "register", "appid": appID}
url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
r = requests.post(url, params=register_data)
jsondata = r.json()

# Grab the part called data from the response, response_data is a list that has only one item in it.
response_data = jsondata['data']
userID = response_data[0].get('value')
print('User ID: %s' % userID)
print('Successfully registerd.')


# functions:
def parse_txt(handle):
    total_result = list()
    note_result = list()
    length_result = list()          # store how many kinds of emotion within every note
    emotion_counter = 0
    for line in handle:
        if line.startswith('*'):     # The symbol of the end of that note
            total_result.append(note_result)
            note_result = list()
            length_result.append(emotion_counter)
            emotion_counter = 0
            continue
    
        chat_data = {
            'cmd': 'chat',
            'appid': appID,
            'userid': userID,
            'text': line,
            'location': ''
        }
    
        url = "http://idc.emotibot.com/api/ApiKey/openapi.php"
        res_chat = requests.post(url,params = chat_data)
        res_chat_jsondata = res_chat.json()       # The response in json format
        if res_chat_jsondata['return'] != 0:      # Return doesn't equal 0 means going wrong
            print(res_chat_jsondata['return_message'])
    
        # Get the reply content and print it
        try:
            reply_data = res_chat_jsondata['data']
            reply_words = reply_data[0].get('value')
            print('Reply: %s' % reply_words)
        except:
            print('No reply.')
                
            
        # Get the emotion info and print it
        emotion_data = res_chat_jsondata['emotion']
        emotion_type = emotion_data[0].get('value')
        emotion_score = emotion_data[0].get('score')
        emotion_score = float(emotion_score)
        print('Type: %s, Score: %.2g' % (emotion_type,emotion_score))
        note_result.append({'Type':emotion_type, 'Score':emotion_score})
        emotion_counter += 1
        
    return [total_result, length_result]

def analyze_txt(total_result,length_result):
    analyzed_result = list()
    for note_index in range(0,len(total_result)):
        # the result of every note, keys in it refer to various types of moods
        single_result = dict()         # {'mood_type1': [times,cum_score]}
        for words in total_result[note_index]:
            if words['Type'] in single_result:
                single_result[words['Type']][0] += 1
                single_result[words['Type']][1] += words['Score']
            else:
                single_result[words['Type']] = [1,words['Score']]
        avg_result = list()
        for key,value in list(single_result.items()):
            avg_score = value[1]/value[0]         # value[0] stands for times, value[1] stands for cum_score
            emotion_proportion = value[0]/length_result[note_index]
            avg_result.append((key,value[0],emotion_proportion,avg_score))
    
        analyzed_result.append(avg_result)
    return analyzed_result

def vectorize(r):
    v_result = np.zeros((len(r),26))      # 26 kinds of emotion, each kind 1 bit
    note_index = 0
    for note in r:
        for emotion in note:
            if emotion[3] > 59 and emotion[0] != '中性':
                e_label = emotions_dict[emotion[0]]
                e_vector = np.zeros((1,26))
                e_vector[0,e_label] = (1+emotion[1]/10) * emotion[2] * emotion[3] / 100
                v_result[note_index] = v_result[note_index] + e_vector
        note_index += 1
    return v_result

def grade(r,std):
    final_result = np.zeros((len(r),26))
    sentence_index = 0
    for sentence in r:
        question_index = 0
        for question in std:
            score = sentence[question > 0] / question[question > 0]
            score = np.mean(score)
            if score > 1.0:
                final_result[sentence_index,question_index] = 3
            elif score > 0.6:
                final_result[sentence_index,question_index] = 2
            elif score > 0.3:
                final_result[sentence_index,question_index] = 1
            question_index += 1
        sentence_index += 1
    return final_result




# Get the name of the standard file
fName = input('Enter the file name:')
try:
    std_fHandle = open(fName,'r')
except:
    print('Cannot open this file.')
    quit()

[std_total_result,std_length_result] = parse_txt(std_fHandle)
std_analyzed_result = analyze_txt(std_total_result,std_length_result)

# Get the name of the diary file
fName = input('Enter the file name:')
try:
    d_fHandle = open(fName,'r')
except:
    print('Cannot open this file.')
    quit()

[d_total_result,d_length_result] = parse_txt(d_fHandle)
d_analyzed_result = analyze_txt(d_total_result,d_length_result)


v_std = vectorize(std_analyzed_result)
v_diary = vectorize(d_analyzed_result)
final_result = grade(v_diary,v_std)
print(np.sum(final_result,axis=1))
