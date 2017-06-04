#!flask/bin/python
import os

import requests
from flask import Flask, json, jsonify, render_template, make_response, request, abort

app = Flask(__name__)

app.static_folder = 'static'
app.template_folder = 'static'

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
    return "I am here"


# Toy API caller
@app.route('/id')
def identity():
    r = requests.get('http://myseniorproject.herokuapp.com/whoAmI')
    d = json.loads(r.text)
    return str(d)


# Toy API responder
@app.route('/germanbot')
def who_am_i():
    return jsonify(identity="Jesus Guzman", age="22", dorms=['Soto', 'Branner', 'Adelfa', 'Roble'])


if __name__ == '__main__':
    app.run()
