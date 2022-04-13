from flask import Flask, request
import requests
import json
import config
import pickle
import random


import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np


global tag
tag=""
from keras.models import load_model
model = load_model('chatbot_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abcd123'

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
#     print(results)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json,d):
    global tag
    # x=ints[0]['probability']
    # if(float(x)<0.80):
    #     tag =""
    # else:
    tag = ints[0]['intent']

    list_of_intents = intents_json['intents']
    flist = []
    for i in list_of_intents:
        if(i['tag']== tag):
            if d=="":
                result = random.choice(i['responses'])
                return result
            else:
                for j in i['responses']:
                    c= j.split("_")
                    # print(c)
                    if c[0] == d:
                        flist.append(c[1])     
                    
    return flist

def chatbot_response(msg,d):
    ints = predict_class(msg, model)
    
    print("\nints")   
    print(ints)
    # print(type(ints[0]['probability']))
    res = getResponse(ints, intents,d)
    return res


#function to access the sender API
def callSenderApi(senderPsid,response,d):
    global tag
    
    print("\n")
    print(response)
    print("\n")
    print(tag)
    
    PAGE_ACCESS_TOKEN =config.PAGE_ACCESS_TOKEN

    if d=="" and (tag == "greeting" or tag == "okay" or tag == "goodbye" or tag == "thanks" or tag == "slang" or tag == "noanswer" or tag == "options"): 
        str1 ="" 
        for ele in response: 
            str1 += ele   
        payload={
            'recipient':{'id': senderPsid},
            'message': {"text":str1},
            'messaging_type':'RESPONSE'
        }
        headers= {'content-type': 'application/json'}
        url = 'https://graph.facebook.com/v13.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
        r = requests.post(url, json=payload, headers= headers)
        print(r.text)
    else:    
        if d=="" and (tag == "places" or tag == "hotels" or tag == "famous_restaurant" or tag == "shopping_malls" or tag == "famous_foods" or tag == "tour-packages" or tag == "best-time-to-travel"):
            payload={
                'recipient':{'id': senderPsid},
                'message': {"text":"⛔ Sorry! Arena is missing. Please provide appropriate arena. I can guide you only for the following districts:\n\n ✅ Dhaka\n ✅ Bandarban\n ✅ Cox's Bazar\n ✅ Sylhet \n ✅ Chittagong"},
                'messaging_type':'RESPONSE'
            }
            headers= {'content-type': 'application/json'}
            url = 'https://graph.facebook.com/v13.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
            r = requests.post(url, json=payload, headers= headers)
            print(r.text) 
        elif d!="" and (tag == "places" or tag == "hotels" or tag == "famous_restaurant" or tag == "shopping_malls" or tag == "famous_foods" or tag == "tour-packages" or tag == "best-time-to-travel"):
            str1 ="" 
           
            for ele in response: 
                str1 += ele 
                str1 += "\n" 

            payload={
                'recipient':{'id': senderPsid},
                'message': {"text":str1},
                'messaging_type':'RESPONSE'
            }
            headers= {'content-type': 'application/json'}
            url = 'https://graph.facebook.com/v13.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
            r = requests.post(url, json=payload, headers= headers)
            print(r.text)
        elif d!="" and (tag != "places" or tag != "hotels" or tag != "famous_restaurant" or tag != "shopping_malls" or tag != "famous_foods" or tag != "tour-packages" or tag != "best-time-to-travel"):
            payload={
                'recipient':{'id': senderPsid},
                'message': {"text":"⛔ Sorry! Please enter proper query with the arena. I can help you only for the following cases:\n\n 🔹 Hotels\n 🔹 Places\n 🔹 Restaurants\n 🔹 Shopping Malls\n 🔹 Famous foods\n 🔹 Tour packages\n 🔹 Best time duration for traveling"},
                'messaging_type':'RESPONSE'
            }
            headers= {'content-type': 'application/json'}
            url = 'https://graph.facebook.com/v13.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
            r = requests.post(url, json=payload, headers= headers)
            print(r.text)
        elif d=="" and (tag != "places" or tag != "hotels" or tag != "famous_restaurant" or tag != "shopping_malls" or tag != "famous_foods" or tag != "tour-packages" or tag != "best-time-to-travel"):    
            payload={
                'recipient':{'id': senderPsid},
                'message': {"text":"⛔ Sorry! Please mention appropriate query with proper arena. I can guide you only for the following districts:\n\n ✅ Dhaka\n ✅ Bandarban\n ✅ Cox's Bazar\n ✅ Sylhet \n ✅ Chittagong.\n\n I can help you only for the following cases:\n\n 🔹 Hotels\n 🔹 Places\n 🔹 Restaurants\n 🔹 Shopping Malls\n 🔹 Famous foods\n 🔹 Tour packages\n 🔹 Best time duration for traveling"},
                'messaging_type':'RESPONSE'
            }
            headers= {'content-type': 'application/json'}
            url = 'https://graph.facebook.com/v13.0/me/messages?access_token={}'.format(PAGE_ACCESS_TOKEN)
            r = requests.post(url, json=payload, headers= headers)
            print(r.text)

#function for handling a message from Messenger
def handleMessage(senderPsid, receivedMessage) :
    
    if 'text' in receivedMessage :
        dis = ["sylhet","Sylhet","sylet","Sylet","Silet","silet","silhet","Silhet", "dhaka", "Dhaka","daka","Daka","Dhk","dhk","dhak","Dhak","Bandarban", "bandarban","bandorbon", "Bandorbon", "Banorbon", "banorbon","Bandarbon","bandarbon","chittagong", "Chittagong","chitagong","citagong","ctg","CTG", "chitagang", "cox's bazar", "Cox's bazar","Cox Bazar","cox bazar","coxs bazar", "Coxs bazar", "coxbazar","Coxbazar","coxsbazar","Coxsbazar","cox","Cox"]
        a= receivedMessage['text']
        d=""
        for i,n in enumerate(dis):
            if n in a:
                d= n

        print("\n")
        print(d)   
        if d.startswith('cox') or d.startswith('Cox'):
            d= "cox's bazar"
        if d.startswith('chi') or d.startswith('Chi') or d.startswith('Ci') or d.startswith('ct'):
            d= "chittagong"
        if d.startswith('ban') or d.startswith('Ban'):
            d= "bandarban"
        if d.startswith('syl') or d.startswith('Syl') or d.startswith('sil') or d.startswith('Sil'):
            d= "sylhet"
        if d.startswith('D') or d.startswith('d') or d.startswith('dhk') or d.startswith('Dhk'):
            d= "dhaka"
        
        
        print("\n")
        print(d)  
        b= chatbot_response(a.lower(),d)
        
        # response = {'Here you go: {}'.format(b)}

        # response ={"text": 'You just sent me: {}'.format(receivedMessage['text'])}

        callSenderApi(senderPsid,b,d)
    else:
        response ={"text": 'This chatbot accepts only text messages'}
        callSenderApi(senderPsid,response,d="")



@app.route('/webhook', methods =["GET","POST"])

def index():
    # if request.method == 'GET':
    VERIFY_TOKEN = 'abcd'

    if 'hub.mode' in request.args:
        mode = request.args.get('hub.mode')
        print(mode)

    if 'hub.challenge' in request.args:
        challenge = request.args.get('hub.challenge')
        print(challenge)
    
    if 'hub.verify_token' in request.args:
        token = request.args.get('hub.verify_token') 
        print(token)

    if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK VERIFIED')

            challange = request.args.get('hub.challenge')

            return challenge, 200
        else:
            return 'ERROR', 403

        
    if request.method == 'POST':
        
        if 'hub.mode' in request.args:
            mode = request.args.get('hub.mode')
            print(mode)

        if 'hub.challenge' in request.args:
            challange = request.args.get('hub.challenge')
            print(challenge)

        if 'hub.verify_token' in request.args:
            token = request.args.get('hub.verify_token') 
            print(token)
        
        if 'hub.mode' in request.args and 'hub.verify_token' in request.args:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')

            if mode == 'subscribe' and token == VERIFY_TOKEN:
                print('WEBHOOK VERIFIED')

                challange = request.args.get('hub.challenge')

                return challenge, 200
            else:
                return 'ERROR', 403

    data = request.data
    
    body = json.loads(data.decode('utf-8'))

    if 'object' in body and body['object'] == 'page' :
        entries = body['entry']
        for entry in entries:
            
            webhookEvent = entry['messaging'][0]
            print(webhookEvent)

            senderPsid = webhookEvent['sender']['id']
            print('Sender PSID: {}'.format(senderPsid))

            recipientPsid = webhookEvent['recipient']['id']
            print('Recipient PSID: {}'.format(recipientPsid))

            timestamp = webhookEvent['timestamp']
            print('timestamp: {}'.format(timestamp))
            print(webhookEvent['message'])

            if 'message' in webhookEvent:
                handleMessage(senderPsid, webhookEvent['message'])

                return 'EVENT_RECEIVED', 200
            else:
                return 'ERROR', 403


@app.route('/', methods = ["GET", "POST"])

def home():

    return 'HOME'

if __name__== '__main__':
    app.run(host = '0.0.0.0', port = '8006', debug= True)    