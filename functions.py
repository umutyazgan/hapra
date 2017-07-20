import socket
import json

#   Socket location. May be different depending on the system.
#   TODO: make socket location independent from the system
server_address = '/var/lib/haproxy/stats'

def get_stat(*parameters):
    """Return HAProxy stats in typed format with specified parameters"""
    #   socket initialization/connection
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(server_address)
    #   send "show stat" command to the socket
    sock.send(b'show stat ' + parameters[0].encode("utf-8") + b' '
                            + parameters[1].encode("utf-8") + b' '
                            + parameters[2].encode("utf-8") + b' typed\n')
    #   receive answer from socket
    #   TODO: get rid of fixed message size(8192)
    data = sock.recv(16384).decode("utf-8")
    sock.close()
    return data

def parse_stat(data):
    """Parse HAProxy stats in typed format into JSON format"""
    #   remove newline character at the end of response string
    data = data[:-1]
    old_identifiers = ['-1','-1','1-']
    entries = data.splitlines()
    dict_list=[]
    for index, entry in enumerate(entries):
        entries[index] = entries[index].split(':')
        entries[index][0] = entries[index][0].split('.')
        identifiers = entries[index][0][:3]
        if identifiers != old_identifiers:
            dict_list.append({})
            old_identifiers = identifiers
        dict_list[-1][entries[index][0][4]] = entries[index][3]
    json_str = json.dumps(dict_list, indent=2)
    return json_str
