#!../flask/bin/python
import socket
from flask import Flask, jsonify, abort, make_response, request, url_for
import csv
import json
import string

server_address = '/var/lib/haproxy/stats'

# create a UDS socket

app = Flask(__name__)

@app.route('/hapra/api/v1.0/show_stat', methods=['GET'])
def show_stat():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(server_address)
    sock.send(b'show stat' + b'\n')
    data = sock.recv(2048).decode("utf-8")
    sock.close()
    data = data[:-1]    #   removing newline character at the end
    entries = data.splitlines()
    for index, line in enumerate(entries):
        entries[index] = line.split(',')
    dict_list = [{} for i in range(len(entries)-1)]
    for index, line in enumerate(entries):
        if index is 0:
            continue
        dict_list[index-1] = dict(zip(entries[0], entries[index])) 
    json_str = json.dumps(dict_list, indent=2)
    return json_str

if __name__ == '__main__':
    app.run(debug=True)
