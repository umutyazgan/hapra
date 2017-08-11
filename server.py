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

@app.route('/hapra/shutdown/session', methods=['GET'])
def shutdown_session():
    """Shutdown session precified by id"""
    session = request.args.get('session')
    ss = shut_session('shutdown session ', session)
    return ss.jsonify()

@app.route('/hapra/shutdown/sessions-server', methods=['GET'])
def shutdown_sessions_server():
    """Shutdown frontend precified by name or id"""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        sss = shut_sessions_server('shutdown sessions server ', 
                                   backend + '/' + server)
    else:
        sss = shut_sessions_server('shutdown sessions server ')
    return sss.jsonify()

@app.route('/hapra/clear/counters', methods=['GET'])
def clear_counters():
    """Clear the max values of the statistics counters in each proxy/server"""
    cc = ccounters('clear counters ')
    return cc.jsonify()

@app.route('/hapra/clear/counters-all', methods=['GET'])
def clear_counters_all():
    """Clear all statistics counters in each proxy/server"""
    cca = ccounters_all('clear counters all ')
    return cca.jsonify()

#  TODO: Add remaining parameters
@app.route('/hapra/clear/table', methods=['GET'])
def clear_table():
    """Remove entries from the stick-table <table>."""
    table = request.args.get('table')
    ct = ctable('clear table ', table)
    return ct.jsonify()

@app.route('/hapra/disable/agent', methods=['GET'])
def disable_agent():
    """Mark the auxiliary agent check as temporarily stopped."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        da = dis_agent('disable agent ', backend + '/' + server)
    else:
        da = dis_agent('disable agent ')
    return da.jsonify()

@app.route('/hapra/disable/frontend', methods=['GET'])
def disable_frontend():
    """Mark the frontend as temporarily stopped."""
    frontend = request.args.get('frontend')
    df = dis_frontend('disable frontend ', frontend)
    return df.jsonify()

@app.route('/hapra/disable/health', methods=['GET'])
def disable_health():
    """Mark the auxiliary health check as temporarily stopped."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        dh = dis_health('disable health ', backend + '/' + server)
    else:
        dh = dis_health('disable health ')
    return dh.jsonify()

@app.route('/hapra/disable/server', methods=['GET'])
def disable_server():
    """Mark the server DOWN for maintenance."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        ds = dis_server('disable server ', backend + '/' + server)
    else:
        ds = dis_server('disable server ')
    return ds.jsonify()

@app.route('/hapra/enable/agent', methods=['GET'])
def enable_agent():
    """Resume auxiliary agent check that was temporarily stopped."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        ea = en_agent('enable agent ', backend + '/' + server)
    else:
        ea = en_agent('enable agent ')
    return ea.jsonify()

@app.route('/hapra/enable/frontend', methods=['GET'])
def enable_frontend():
    """Resume a frontend which was temporarily stopped."""
    frontend = request.args.get('frontend')
    ef = en_frontend('enable frontend ', frontend)
    return ef.jsonify()

@app.route('/hapra/enable/health', methods=['GET'])
def enable_health():
    """Resume a primary health check that was temporarily stopped."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        eh = en_health('enable health ', backend + '/' + server)
    else:
        eh = en_health('enable health ')
    return eh.jsonify()

@app.route('/hapra/enable/server', methods=['GET'])
def enable_server():
    """Mark the server UP."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        es = en_server('enable server ', backend + '/' + server)
    else:
        es = en_server('enable server ')
    return es.jsonify()

@app.route('/hapra/get/weight', methods=['GET'])
def get_weight():
    """Report the current weight and the initial weight of <server>."""
    backend = request.args.get('backend')
    server = request.args.get('server')
    if backend and server:
        gw = g_weight('get weight ', backend + '/' + server)
    else:
        gw = g_weight('get weight')
    return gw.jsonify()

@app.route('/hapra/help', methods=['GET'])
def help():
    """Print the list of known keywords and their basic usage."""
    h = hp('help')
    return h.jsonify()

if __name__ == '__main__':
    app.run(debug=True)
