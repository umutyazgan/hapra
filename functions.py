import socket
import json

#   Socket location. May be different depending on the system.
#   TODO: make socket location independent from the system
server_address = '/var/lib/haproxy/stats'

class socket_command(object):
    def __init__(self, *args):
        """Return HAProxy stats in typed format with specified parameters"""
        arg_count = len(locals()['args'])
        #   socket initialization/connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(server_address)
        command_string = args[0]
        for i in range(1, arg_count):
            if args[i] is not None:
                command_string += (args[i] + ' ')
        command_string += '\n'
        sock.send(command_string.encode('utf-8'))
        #   receive answer from socket
        #   TODO: get rid of fixed message size(16384)
        self.data = sock.recv(16384).decode('utf-8')
        sock.close()

class env(socket_command):
    def jsonify(self):
        """Parse HAProxy environment variables into JSON format"""
        data = self.data[:-1]
        if data == "Variable not found\n":
            return json.dumps(None, indent=2)
        entries=data.splitlines()
        env_dict = {}
        for entry in entries:
            entry = entry.split('=', 1)
            env_dict[entry[0]]=entry[1]
        return json.dumps(env_dict, indent=2)

class stat(socket_command):
    def __init__(self, *args):
        """Return HAProxy stats in typed format with specified parameters"""
        arg_count = len(locals()['args'])
        #   socket initialization/connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(server_address)
        #   send "show stat" command to the socket
        sock.send(b'show stat\n')
        self.csv_data = sock.recv(16384).decode()
        sock.close()
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(server_address)
        command_string = args[0]
        for i in range(1, arg_count):
            if args[i] is not None:
                command_string += (args[i] + ' ')
        command_string += 'typed'
        command_string += '\n'
        sock.send(command_string.encode('utf-8'))
        #   receive answer from socket
        #   TODO: get rid of fixed message size(16384)
        self.data = sock.recv(16384).decode('utf-8')
        sock.close()
    def jsonify(self):
        """Parse HAProxy stats in typed format into JSON format"""
        #   get field names from csv output
        fnames = self.csv_data[2:].splitlines()[0].split(',')
        #   remove newline character at the end of typed output string
        data = self.data[:-1]
        #   return null in case of "No such proxy" response.
        #   TODO(?): Maybe return a differen HTTP status code?
        if data == 'No such proxy.\n':
            return json.dumps(None, indent=2)
        #   remove empty field at the end of fnames list
        fnames = fnames[:-1]
        #   initial values for identifiers(first three parts of the first column of
        #   each entry). -1 is choosen because none of the first three parts can be
        #   -1 by default, which guarantees detection of the first object by the
        #   2nd if statement in the for loop below
        old_identifiers = ['-1','-1','-1']
        #   a list of sets to keep track of the distinct process numbers
        pno_sets = []
        #   split data into a list of entries(lines)
        entries = data.splitlines()
        #   obj_count will be necessary to determine number of json objects in the 
        #   dict_list[] list.
        obj_count = 0
        #   we need to hold indexes for entries[] list where identifiers change so
        #   we can determine where json objects start and end in the entries[] list
        obj_start_indexes = []
        # TODO: These 2 for loops scan the whole entries list 2 times. Maybe I can
        #       combine them into a single for loop and scan the list only once
        #   This loop parses each entry by first spliting it to 3 columns seperated
        #   by colons and then spliting the first column into 6 seperate elements. 
        #   Then it counts the number of json objects needed to store all entries.
        #   It also stores starting/ending positions of these objects in a list.
        for index, entry in enumerate(entries):
            #   split entries into sub-lists
            entries[index] = entries[index].split(':', 3)
            entries[index][0] = entries[index][0].split('.')
            #   check if identifiers have changed
            identifiers = entries[index][0][:3]
            if identifiers != old_identifiers:
                # if identifiers changed, then this is a new json object. Increase
                # obj_count, store starting index and set new identifiers.
                obj_count += 1
                obj_start_indexes.append(index)
                old_identifiers = identifiers
                #  for each object, create a new set of process numbers('pno's),
                #  and add the set to the pno_sets list
                pno_set = set()
                pno_sets.append(pno_set)
            #  add pno of entry to pno_set of the object. Set will ensure that each
            #  pno is added only once.
            pno_sets[obj_count-1].add(entries[index][0][5])
        #   set last index + 1 as ending index of the last json object
        obj_start_indexes.append(len(entries))
        #   initialize a list of dictionaries, using obj_count as its size. This
        #   will represent out json return value
        dict_list = [{} for obj in range(obj_count)]
        # this loop scans each object and sets identifying values: type, iid and 
        # sid. Also creates and fills a list of "fields" sub-objects. 1 "fields"
        # object per pno(process_number). Note that pno itself is also a field-name
        for i in range(obj_count):
            #   set index to starting entry index of each object
            index = obj_start_indexes[i]
            #   check first element of the first column and set "type" field
            if entries[index][0][0] is 'F':
                dict_list[i]['type'] = 'Frontend'
            elif entries[index][0][0] is 'B':
                dict_list[i]['type'] = 'Backend'
            elif entries[index][0][0] is 'L':
                dict_list[i]['type'] = 'Listener'
            elif entries[index][0][0] is 'S':
                dict_list[i]['type'] = 'Server'
            else:
                dict_list[-1]['type'] = 'unknown'
                print("Unknown object type!\n")
                # TODO: handle this error
            #  set "iid" and "sid" fields to 2nd and 3rd elements respectively
            dict_list[i]['iid'] = entries[index][0][1]
            dict_list[i]['sid'] = entries[index][0][2]
            #  turn sets into sorted lists so sub-objects in the fields list of the
            #  json output is also ordered
            pno_sets[i] = sorted(pno_sets[i])
            #  initialize "fields" value as a list of dictionaries(sub-objects),
            #  set the "pno" values at the initialization
            dict_list[i]['fields'] = [{'pno': pno} for pno in pno_sets[i]]
            #   this inner loop scans all possible field-names and checks if any of 
            #   these names exist in the current object. All field-values are 
            #   initialized as null and changed later if enountered in the current 
            #   object
            for fname in fnames:
                #   initialize field-values as null for each pno
                for pno in range(len(dict_list[i]['fields'])):
                    dict_list[i]['fields'][pno][fname] = None
                #   scan whole object for matching field-name
                for j in range(obj_start_indexes[i+1]-obj_start_indexes[i]):
                    #  if found, set the field-value accordingly
                    if fname == entries[index+j][0][4]:
                        pno = int(entries[index+j][0][5])-1
                        dict_list[i]['fields'][pno][fname] = entries[index+j][3]
                    #   else, leave null
        #   turn json style formated dict_list into a json string
        return json.dumps(dict_list, indent=2)

def parse_sess(data):
    """Parse session information into JSON format"""
    data = data[:-1]
    entries = data.splitlines()
    for index, entry in enumerate(entries):
        entries[index] = entries[index].split(' ')
#  TODO: combine these two into a single func
def parse_sess_id(data):
    """Parse session information into JSON format"""
    pass
