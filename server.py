#!../flask/bin/python

#   TODO: this application needs root privileges to run. Make it work without it.

import socket
from flask import Flask, jsonify, abort, make_response, request, url_for
import csv
import json
import string
from functions import *

app = Flask(__name__)

#   TODO: add timeout mechanism
@app.route('/hapra/show/stat', methods=['GET'])
def show_stat():
    """Return output of "show stat typed" socket command as a JSON string"""
    iid = request.args.get('iid')
    t   = request.args.get('type')
    sid = request.args.get('sid')
    s = stat('show stat ', iid, t, sid)
    return s.jsonify()

@app.route('/hapra/show/env', methods=['GET'])
def show_env():
    """Return output of "show env" socket command as a JSON string"""
    name = request.args.get('name')
    e = env('show env ', name)
    return e.jsonify()

@app.route('/hapra/show/backend', methods=['GET'])
def show_backend():
    """Return output of "show backend" socket command as a JSON string """
    b = backend('show backend ')
    return b.jsonify()

#@app.route('/hapra/show/sess', methods=['GET'])
#def show_sess():
#    """Return output of "show sess" socket command as a JSON string """
#    data = get_output('show sess ')
#    return parse_sess(data)

#@app.route('/hapra/show/sess/<sess_id>', methods=['GET'])
#def show_sess_id(sess_id):
#    """Return output of "show sess <id>" socket command as a JSON string """
#    data = get_output('show sess {} '.format(sess_id))
#    return parse_sess_id(data)

if __name__ == '__main__':
    app.run(debug=True)
