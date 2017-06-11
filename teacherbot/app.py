#!flask/bin/python
import os

import requests
import thread
from flask import Flask, json, jsonify, render_template, make_response, request, abort
from TeacherBot import TeacherBot

app = Flask(__name__)

teacherBot = TeacherBot()

app.static_folder = 'static'
app.template_folder = 'static'
relay_server_url = 'http://chatio.ngrok.io'
login_url = relay_server_url + '/admin/botLogin'
get_users_url = relay_server_url + "/botUsers"
get_user_info_url = relay_server_url + "/userInfo"
send_message_url = relay_server_url + "/botSendMessage"

teacherbot_credentials = {'username': 'teacherbot', 'password': 'teacherbot'}

teacherbot_id = None
teacherbot_cookies = None
teacherbot_user_ids = []

# Detect if deployed on Heroku
if 'DYNO' in os.environ:
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(_):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.route('/')
def main_site():
    return render_template('main.html')


@app.route('/moviebot/sendMessage',  methods=['GET', 'POST'])
def receive_message():
	print("moviebot_receive_message")
	req = {
		'userId': request.json['userId'],
		'botId': request.json[u'botId'],
		'text': request.json['text']
	}
	thread.start_new_thread(process_message, (req,))
	return jsonify(message='--ACK--')


def login_bots():
    server_response = requests.post(login_url, json=teacherbot_credentials)
    status_code = str(server_response.status_code)
    response_reason = server_response.reason
    content = server_response.json()
    cookies = server_response.cookies

    print('Respone status code: ' + status_code)
    print('Respone reason     : ' + response_reason)
    print('Respone text       : ' + str(content))

    if server_response.status_code != 200:
        print('Error logging in')
    else:
    	global teacherbot_id
    	global teacherbot_cookies
        teacherbot_id = content['id']
        teacherbot_cookies = cookies


def get_users():
	global teacherbot_cookies
	server_request = requests.get(get_users_url, cookies=teacherbot_cookies)
	status_code = str(server_request.status_code)
	response_reason = server_request.reason
	content = server_request.json()

	print('Respone status code: ' + status_code)
	print('Respone reason     : ' + response_reason)
	print('Respone content    : ' + str(content))

	if server_request.status_code != 200:
	    print('Error getting users ')
	else:
	    global teacherbot_user_ids
	    teacherbot_user_ids = content['users']
	    print("user ids: " + str(teacherbot_user_ids))


def send_message(msg, user_id, bot_id):
	global teacherbot_cookies
	params = {
	    'botId': bot_id,
	    'userId': user_id,
	    'type': 'text',
	    'text': msg
	}

	server_request = requests.post(send_message_url, cookies=teacherbot_cookies, json=params)
	status_code = str(server_request.status_code)
	response_reason = server_request.reason
	content = server_request

	print('Respone status code: ' + status_code)
	print('Respone reason     : ' + response_reason)
	print('Respone content    : ' + str(content))

	if server_request.status_code != 200:
	    print('Error sending message ')


# def send_multiple_choice_message(options, user_id, bot_id):
#     global moviebot_cookies
#     params = {
#         'botId': bot_id,
#         'userId': user_id,
#         'type': 'mc',
#         'options': options
#     }
#     server_request = requests.post(send_message_url, cookies=moviebot_cookies, json=params)

#     if app.config['DEBUG']:
#         print('send_multiple_choice_message(options, user_id, bot_id)')
#         status_code = str(server_request.status_code)
#         response_reason = server_request.reason
#         content = server_request
#         print('Respone status code: ' + status_code)
#         print('Respone reason     : ' + response_reason)
#         print('Respone content    : ' + str(content))

#         if server_request.status_code != 200:
#             print('Error sending message.')


def get_user_info(user_id, bot_id):
	global teacherbot_cookies
	url = get_user_info_url + '/' + bot_id + '/' + user_id + '/basic'
	server_request = requests.get(url, cookies=teacherbot_cookies)
	status_code = str(server_request.status_code)
	response_reason = server_request.reason
	content = server_request.json()

	print('Respone status code: ' + status_code)
	print('Respone reason     : ' + response_reason)
	print('Respone content    : ' + str(content))

	if server_request.status_code != 200:
	    print('Error getting user info ')

	print('user infos: ' + str(content))

def process_message(req):
	print "I am processing your message"
	response = teacherBot.getResponse(req['text'])
	send_message(response, req['userId'], req['botId'])



if __name__ == '__main__':

    # log in severs
    login_bots()

    # get user ids
    get_users()

    # start bots
    app.run()







