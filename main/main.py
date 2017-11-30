import socket
from flask import Flask, jsonify, abort, make_response, request, Response, url_for
import csv
import json
import string
from .functions import *

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')

@app.route('/test/', methods=['GET'])
def test():
    """TEST"""
#    test_str = str(app.config['READ_ONLY'])
    return "True"

#  TODO: add timeout mechanism

#  NOTE: jsonify() method used in this file is NOT the jsonify()
#        method from Flask framework! I know it's a horrible naming
#        choice. Those methods will be rewritten in the future.
@app.route('/hapra/show/stat', methods=['GET'])
def show_stat():
    """Dump statistics using the extended typed output format."""
    iid = request.args.get('iid')
    t   = request.args.get('type')
    sid = request.args.get('sid')
    query_strings = filter(None, [iid, t, sid])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    s = stat('show stat ', iid, t, sid)
    return Response(s.jsonify(), mimetype='application/json')

@app.route('/hapra/show/env', methods=['GET'])
def show_env():
    """Return output of "show env" socket command as a JSON string"""
    name = request.args.get('name')
    if name and ';' in name:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
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
    if backend and ';' in backend:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    ss = servers_state('show servers state ', backend)
    return ss.jsonify()

@app.route('/hapra/show/pools', methods=['GET'])
def show_pools():
    """Return output of "show pools" socket command as a JSON string"""
    p = pools('show pools ')
    return p.jsonify()

@app.route('/hapra/show/table', methods=['GET'])
def show_table():
    """Dump general information on all known stick-tables."""
    t = table('show table ')
    return t.jsonify()

#  TODO: maybe find a better name?
@app.route('/hapra/show/table-detail', methods=['GET'])
def show_table_detail():
    """Dump contents of stick-table <name>."""
    name = request.args.get('name')
    typ = request.args.get('type')
    if typ == None:
        typ = ''
    operator = request.args.get('operator')
    value = request.args.get('value')
    key = request.args.get('key')
    query_strings = filter(None, [name, typ, operator, value, key])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if key:
        td = table_detail('show table ', name, 'key ' + key)
    else:
        td = table_detail('show table ', name, 'data.'+typ, operator, value)
    return td.jsonify()

@app.route('/hapra/show/sess', methods=['GET'])
def show_sess():
    """Dump all known sessions."""
    ss = s_sess('show sess ')
    return ss.jsonify()

#@app.route('/hapra/show/sess/<sess_id>', methods=['GET'])
#def show_sess_id(sess_id):
#    """Return output of "show sess <id>" socket command as a JSON string """
#    data = get_output('show sess {} '.format(sess_id))
#    return parse_sess_id(data)

@app.route('/hapra/shutdown/frontend', methods=['GET', 'POST'])
def shutdown_frontend():
    """Shutdown frontend precified by name or id"""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    frontend = request.args.get('frontend')
    if frontend and ';' in frontend:
        return "Usage of ';' in parameters is not allowed"
    sf = shut_frontend('shutdown frontend ', frontend)
    return sf.jsonify()

@app.route('/hapra/shutdown/session', methods=['GET', 'POST'])
def shutdown_session():
    """Shutdown session precified by id"""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    session = request.args.get('session')
    if session and ';' in session:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    ss = shut_session('shutdown session ', session)
    return ss.jsonify()

@app.route('/hapra/shutdown/sessions-server', methods=['GET', 'POST'])
def shutdown_sessions_server():
    """Shutdown frontend precified by name or id"""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        sss = shut_sessions_server('shutdown sessions server ',
                                   backend + '/' + server)
    else:
        sss = shut_sessions_server('shutdown sessions server ')
    return sss.jsonify()

@app.route('/hapra/clear/counters', methods=['GET', 'POST'])
def clear_counters():
    """Clear the max values of the statistics counters in each proxy/server"""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    cc = ccounters('clear counters ')
    return cc.jsonify()

@app.route('/hapra/clear/counters/all', methods=['GET', 'POST'])
def clear_counters_all():
    """Clear all statistics counters in each proxy/server"""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    cca = ccounters_all('clear counters all ')
    return cca.jsonify()

@app.route('/hapra/clear/table', methods=['GET', 'POST'])
def clear_table():
    """Remove entries from the stick-table <table>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    name = request.args.get('name')
    typ = request.args.get('type')
    if typ == None:
        typ = ''
    operator = request.args.get('operator')
    value = request.args.get('value')
    key = request.args.get('key')
    query_strings = filter(None, [name, typ, operator, value, key])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if key:
        td = table_detail('clear table ', name, 'key ' + key)
    else:
        td = table_detail('clear table ', name, 'data.'+typ, operator, value)
    return td.jsonify()

@app.route('/hapra/disable/agent', methods=['GET', 'POST'])
def disable_agent():
    """Mark the auxiliary agent check as temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        da = dis_agent('disable agent ', backend + '/' + server)
    else:
        da = dis_agent('disable agent ')
    return da.jsonify()

@app.route('/hapra/disable/frontend', methods=['GET', 'POST'])
def disable_frontend():
    """Mark the frontend as temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    frontend = request.args.get('frontend')
    if frontend and ';' in frontend:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    df = dis_frontend('disable frontend ', frontend)
    return df.jsonify()

@app.route('/hapra/disable/health', methods=['GET', 'POST'])
def disable_health():
    """Mark the auxiliary health check as temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        dh = dis_health('disable health ', backend + '/' + server)
    else:
        dh = dis_health('disable health ')
    return dh.jsonify()

@app.route('/hapra/disable/server', methods=['GET', 'POST'])
def disable_server():
    """Mark the server DOWN for maintenance."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ds = dis_server('disable server ', backend + '/' + server)
    else:
        ds = dis_server('disable server ')
    return ds.jsonify()

@app.route('/hapra/enable/agent', methods=['GET', 'POST'])
def enable_agent():
    """Resume auxiliary agent check that was temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ea = en_agent('enable agent ', backend + '/' + server)
    else:
        ea = en_agent('enable agent ')
    return ea.jsonify()

@app.route('/hapra/enable/frontend', methods=['GET', 'POST'])
def enable_frontend():
    """Resume a frontend which was temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    if frontend and ';' in frontend:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    frontend = request.args.get('frontend')
    ef = en_frontend('enable frontend ', frontend)
    return ef.jsonify()

@app.route('/hapra/enable/health', methods=['GET', 'POST'])
def enable_health():
    """Resume a primary health check that was temporarily stopped."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        eh = en_health('enable health ', backend + '/' + server)
    else:
        eh = en_health('enable health ')
    return eh.jsonify()

@app.route('/hapra/enable/server', methods=['GET', 'POST'])
def enable_server():
    """Mark the server UP."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
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
    query_strings = filter(None, [backend, server])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
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

@app.route('/hapra/set/maxconn/frontend', methods=['GET', 'POST'])
def set_maxconn_frontend():
    """Dynamically change the specified frontend's maxconn setting."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    frontend = request.args.get('frontend')
    value = request.args.get('value')
    query_strings = filter(None, [frontend, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    smf = s_maxconn_frontend('set maxconn frontend ', frontend, value)
    return smf.jsonify()

#  TODO: prevent negative values
@app.route('/hapra/set/maxconn/server', methods=['GET', 'POST'])
def set_maxconn_server():
    """Dynamically change the specified server's maxconn setting."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    value = request.args.get('value')
    query_strings = filter(None, [backend, server, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        sms = s_maxconn_server('set maxconn server ',
                               backend + '/' + server, value)
    else:
        sms = s_maxconn_server('set maxconn server ', value)
    return sms.jsonify()

@app.route('/hapra/set/maxconn/global', methods=['GET', 'POST'])
def set_maxconn_global():
    """Dynamically change the global maxconn setting."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    value = request.args.get('value')
    if value and ';' in value:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    smg = s_maxconn_global('set maxconn global ', value)
    return smg.jsonify()

@app.route('/hapra/set/rate-limit/connections/global', methods=['GET', 'POST'])
def set_ratelimit_connections_global():
    """Change the process-wide connection rate limit."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    value = request.args.get('value')
    if value and ';' in value:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    srcg = s_ratelimit_connections_global('set rate-limit connections global ',
                                          value)
    return srcg.jsonify()

@app.route('/hapra/set/rate-limit/http-compression/global', methods=['GET', 'POST'])
def set_ratelimit_httpcompression_global():
    """Change the maximum input compression rate."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    value = request.args.get('value')
    if value and ';' in value:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    srhg = s_ratelimit_httpcompression_global(
           'set rate-limit http-compression global ', value)
    return srhg.jsonify()

@app.route('/hapra/set/rate-limit/sessions/global', methods=['GET', 'POST'])
def set_ratelimit_sessions_global():
    """Change the process-wide session rate limit."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    value = request.args.get('value')
    if value and ';' in value:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    srsg = s_ratelimit_sessions_global('set rate-limit sessions global ',
                                          value)
    return srsg.jsonify()

@app.route('/hapra/set/rate-limit/ssl-sessions/global', methods=['GET', 'POST'])
def set_ratelimit_sslsessions_global():
    """Change the process-wide SSL session rate limit."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    value = request.args.get('value')
    if value and ';' in value:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    srsg = s_ratelimit_sslsessions_global('set rate-limit ssl-sessions global ',
                                          value)
    return srsg.jsonify()

@app.route('/hapra/set/server/addr', methods=['GET', 'POST'])
def set_server_addr():
    """Replace the current IP address of a server by the one provided."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    ip = request.args.get('ip')
    port = request.args.get('port')
    query_strings = filter(None, [backend, server, ip, port])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server and port:
        ssa = s_server_addr('set server ', backend + '/' + server, 'addr', ip,
                            'port', port)
    elif backend and server:
        ssa = s_server_addr('set server ', backend + '/' + server, 'addr', ip)
    elif port:
        ssa = s_server_addr('set server ', 'addr', ip, 'port', port)
    else:
        ssa = s_server_addr('set server ', 'addr', ip)
    return ssa.jsonify()

@app.route('/hapra/set/server/agent', methods=['GET', 'POST'])
def set_server_agent():
    """Force a server's agent to a new state."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    state = request.args.get('state')
    query_strings = filter(None, [backend, server, state])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ssh = s_server_agent('set server ', backend + '/' + server, 'agent',
                                state)
    else:
        ssh = s_server_agent('set server ', 'agent', state)
    return ssh.jsonify()

@app.route('/hapra/set/server/health', methods=['GET', 'POST'])
def set_server_health():
    """Force a server's health to a new state."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    state = request.args.get('state')
    query_strings = filter(None, [backend, server, state])
    if any(';' in qstr for qstr in query_strings):
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ssh = s_server_health('set server ', backend + '/' + server, 'health',
                                state)
    else:
        ssh = s_server_health('set server ', 'health', state)
    return ssh.jsonify()

@app.route('/hapra/set/server/check-port', methods=['GET', 'POST'])
def set_server_checkport():
    """Change the port used for health checking to <port>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    port = request.args.get('port')
    query_strings = filter(None, [backend, server, port])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ssc = s_server_checkport('set server ', backend + '/' + server,
                                'check-port', port)
    else:
        ssc = s_server_checkport('set server ', 'check-port', port)
    return ssc.jsonify()

@app.route('/hapra/set/server/state', methods=['GET', 'POST'])
def set_server_state():
    """Force a server's administrative state to a new state."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    state = request.args.get('state')
    query_strings = filter(None, [backend, server, state])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        sss = s_server_state('set server ', backend + '/' + server,
                                'state', state)
    else:
        sss = s_server_state('set server ', 'state', state)
    return sss.jsonify()

@app.route('/hapra/set/server/weight', methods=['GET', 'POST'])
def set_server_weight():
    """Change a server's weight to the value passed in argument."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    weight = request.args.get('weight')
    query_strings = filter(None, [backend, server, weight])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        ssw = s_server_weight('set server ', backend + '/' + server,
                                'weight', weight)
    else:
        ssw = s_server_weight('set server ', 'weight', weight)
    return ssw.jsonify()

@app.route('/hapra/set/weight', methods=['GET', 'POST'])
def set_weight():
    """Change a server's weight to the value passed in argument."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    backend = request.args.get('backend')
    server = request.args.get('server')
    weight = request.args.get('weight')
    query_strings = filter(None, [backend, server, weight])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    if backend and server:
        sw = s_server_weight('set weight ', backend + '/' + server, weight)
    else:
        sw = s_server_weight('set weight ', weight)
    return sw.jsonify()

@app.route('/hapra/add/acl', methods=['GET', 'POST'])
def add_acl():
    """Add an entry into the acl <acl>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    acl = request.args.get('acl')
    pattern = request.args.get('pattern')
    query_strings = filter(None, [acl, pattern])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    aa = a_acl('add acl ', acl, pattern)
    return aa.jsonify()

@app.route('/hapra/clear/acl', methods=['GET', 'POST'])
def clear_acl():
    """Remove all entries from the acl <acl>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    if acl and ';' in acl:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    acl = request.args.get('acl')
    ca = c_acl('clear acl ', acl)
    return ca.jsonify()

@app.route('/hapra/del/acl', methods=['GET', 'POST'])
def del_acl():
    """Delete all the acl entries from the acl <acl> corresponding to the key
        <key>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    acl = request.args.get('acl')
    key = request.args.get('key')
    query_strings = filter(None, [acl, key])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    da = d_acl('del acl ', acl, key)
    return da.jsonify()

@app.route('/hapra/get/acl', methods=['GET'])
def get_acl():
    """Lookup the value <value> in the in the ACL <acl>."""
    acl = request.args.get('acl')
    value = request.args.get('value')
    query_strings = filter(None, [acl, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    ga = g_acl_map('get acl ', acl, value)
    return ga.jsonify()

@app.route('/hapra/show/acl', methods=['GET'])
def show_acl():
    """Dump info about acl converters."""
    acl = request.args.get('acl')
    if acl and ';' in acl:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    sa = s_acl('show acl ', acl)
    return sa.jsonify()

#  TODO: map commands doesn't work with map #<id>'s.
@app.route('/hapra/show/map', methods=['GET'])
def show_map():
    """Dump info about map converters."""
    mp = request.args.get('map')
    if mp and ';' in mp:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    sm = s_map('show map ', mp)
    return sm.jsonify()

@app.route('/hapra/add/map', methods=['GET', 'POST'])
def add_map():
    """Add an entry into the map <map>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    mp = request.args.get('map')
    key = request.args.get('key')
    value = request.args.get('value')
    query_strings = filter(None, [mp, key, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    am = a_map('add map ', mp, key, value)
    return am.jsonify()

@app.route('/hapra/clear/map', methods=['GET', 'POST'])
def clear_map():
    """Remove all entries from the map <map>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    mp = request.args.get('map')
    if mp and ';' in mp:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    cm = c_map('clear map ', mp)
    return cm.jsonify()

@app.route('/hapra/del/map', methods=['GET', 'POST'])
def del_map():
    """Delete all the map entries from the map <map> corresponding to the key
        <key>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    mp = request.args.get('map')
    key = request.args.get('key')
    query_strings = filter(None, [mp, key])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    dm = d_map('del map ', mp, key)
    return dm.jsonify()

@app.route('/hapra/get/map', methods=['GET'])
def get_map():
    """Lookup the value <value> in the in the map <map>."""
    mp = request.args.get('map')
    value = request.args.get('value')
    query_strings = filter(None, [mp, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    gm = g_acl_map('get map ', mp, value)
    return gm.jsonify()

@app.route('/hapra/set/map', methods=['GET', 'POST'])
def set_map():
    """Modify the value corresponding to each key <key> in a map <map>."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    mp = request.args.get('map')
    key = request.args.get('key')
    value = request.args.get('value')
    query_strings = filter(None, [mp, key, value])
    if any(';' in qstr for qstr in query_strings):
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    sm = se_map('set map ', mp, key, value)
    return sm.jsonify()

@app.route('/hapra/set/timeout/cli', methods=['GET', 'POST'])
def set_timeout_cli():
    """Change the CLI interface timeout for current connection."""
    if app.config['READ_ONLY']:
        message = "Error: Read only mode is enabled"
        response = {'status':'failure','code':'405','message':message}
        return json.dumps(response, indent=2), 405
    delay = request.args.get('delay')
    if delay and ';' in delay:
        message = "Error: ';' Using character in query strings is not allowed."
        response = {'status':'failure','code':'403','message':message}
        return json.dumps(response, indent=2), 403
    stc = s_timeout_cli('set timeout cli ', delay)
    return stc.jsonify()

#if __name__ == '__main__':
    #app.run(host='0.0.0.0')
