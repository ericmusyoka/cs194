from flask import Flask
from flask import jsonify
from flask import request
import json
import requests
import threading

app = Flask(__name__)

def send_message(message, uid, bid):
    data = {
        "username": "teacherbot",
        "password": "teacherbot"
    }
    #"http://protected-ridge-46546.herokuapp.com/admin/botLogin"
    response = requests.post("http://chatio.ngrok.io/admin/botLogin", json=data)
    data = {
        "type": "text",
        "userId": uid,
        "botId": bid,
        "text": message
    }
    requests.post("http://chatio.ngrok.io/botSendMessage", json=data, cookies=response.cookies)

@app.route('/sendMessage', methods=['GET', 'POST'])
def receive_message():
    message = request.json['text']
    uid = request.json['userId']
    bid = request.json['botId']
    threading.Thread(target=send_message, args=(message, uid, bid,)).start()
    return jsonify(message='--ACK--')

if __name__ == '__main__':
    data = {
        "username": "teacherbot",
        "password": "teacherbot"
    }
    print("Before login.")
    #"http://protected-ridge-46546.herokuapp.com/admin/botLogin"
    response = requests.post("http://chatio.ngrok.io/admin/botLogin", json=data)
    global bot_cookies
    bot_cookies = response.cookies
    print("After login.")
    app.run(debug=True)







