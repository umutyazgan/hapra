#!../flask/bin/python

#   TODO: this application needs root privileges to run. Make it work without it.

import socket
from flask import Flask, jsonify, abort, make_response, request, url_for
import csv
import json
import string

#   Socket location. May be different depending on the system.
#   TODO: make socket location independent from the system
server_address = '/var/lib/haproxy/stats'

app = Flask(__name__)

#   TODO: add timeout mechanism
#   TODO: add parameters
@app.route('/hapra/show/stat', methods=['GET'])
def show_stat():
    """Return output of "show stat" socket command as a JSON string(instead of CSV.)"""
    #   socket initialization/connection
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(server_address)
    #   send "show stat" command to the socket
    sock.send(b'show stat' + b'\n')
    #   receive answer from socket
    #   TODO: get rid of fixed message size(4096)
    data = sock.recv(4096).decode("utf-8")
    sock.close()
    #   remove newline character at the end of response string
    data = data[:-1]
    #   split response string into a list of lines,
    entries = data.splitlines()
    #   then split lines into a list of entries
    for index, line in enumerate(entries):
        entries[index] = line.split(',')
    #   create a list of dictionaries to resemble json formated output 
    dict_list = [{} for i in range(len(entries)-1)]
    #   create dictionaries by zipping lines together
    for index, line in enumerate(entries):
        if index is 0:
            continue
        dict_list[index-1] = dict(zip(entries[0], entries[index])) 
    #   turn list of dictionaries into a json formated string with 2 space indent
    json_str = json.dumps(dict_list, indent=2)
    return json_str

if __name__ == '__main__':
    app.run()
