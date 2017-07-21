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
    (data, csv_data) = get_stat(iid, t, sid)
    return parse_stat(data, csv_data)

if __name__ == '__main__':
    app.run(debug=True)
