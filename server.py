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
    """Return output of "show backend" socket command as a JSON string"""
    b = backend('show backend ')
    return b.jsonify()

@app.route('/hapra/show/info', methods=['GET'])
def show_info():
    """Return output of "show info typed" socket command as a JSON string"""
    i = info('show info ')
    return i.jsonify()

@app.route('/hapra/show/servers-state', methods=['GET'])
def show_servers_state():
    """Return output of "show servers state" socket command as a JSON string"""
    backend = request.args.get('backend')
    ss = servers_state('show servers state ', backend)
    return ss.jsonify()

@app.route('/hapra/show/pools', methods=['GET'])
def show_pools():
    """Return output of "show pools" socket command as a JSON string"""
    p = pools('show pools ')
    return p.jsonify()

@app.route('/hapra/show/table', methods=['GET'])
def show_table():
    """Return output of "show table" socket command as a JSON string"""
    t = table('show table ')
    return t.jsonify()

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

@app.route('/hapra/shutdown/frontend', methods=['GET'])
def shutdown_frontend():
    """Shutdown frontend precified by name or id"""
    frontend = request.args.get('frontend')
    sf = shut_frontend('shutdown frontend ', frontend)
    return sf.jsonify()

if __name__ == '__main__':
    app.run(debug=True)
