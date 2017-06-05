#!flask/bin/python
import os

import requests
from flask import Flask, json, jsonify, render_template, make_response, request, abort
from TeacherBot import TeacherBot

app = Flask(__name__)

app.static_folder = 'static'
app.template_folder = 'static'

teacherBot = TeacherBot()

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
    return teacherBot.getResponse("Hi")


@app.route('/teacherbot/', methods=['POST'])
def getresponse():
    return jsonify(message='--ACK--')

if __name__ == '__main__':
    app.run()

