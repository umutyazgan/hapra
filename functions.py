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

class backend(socket_command):
    def jsonify(self):
        data = self.data[:-1]
        data = data.splitlines()
        del data[0]
        be_dict = {}
        for i, line in enumerate(data):
            be_dict[i] = line
        return json.dumps(be_dict, indent=2)

class info(socket_command):
    def __init__(self, *args):
        """Return HAProxy info in typed format with specified parameters"""
        arg_count = len(locals()['args'])
        #   socket initialization/connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(server_address)
        command_string = args[0]
        for i in range(1, arg_count):
            if args[i] is not None:
                command_string += (args[i] + ' ')
        command_string += ' typed '
        command_string += '\n'
        sock.send(command_string.encode('utf-8'))
        #   receive answer from socket
        #   TODO: get rid of fixed message size(16384)
        self.data = sock.recv(16384).decode('utf-8')
        sock.close()
    def jsonify(self, *args):
        entries = self.data[:-1]
        entries = entries.splitlines()
        dict_list = []
        for index, entry in enumerate(entries):
            entries[index] = entries[index].split(':',3)
            entries[index][0] = entries[index][0].split('.')
            if len(dict_list) == 0:
                dict_list.append({'pno': entries[index][0][2]})
            for d in dict_list:
                if d['pno'] == entries[index][0][2]:
                    d[entries[index][0][1]] = entries[index][3]
                    pno_found = True
                    break
                else:
                    pno_found = False
            if pno_found is False:
                dict_list.append({'pno': entries[index][0][2],
                                  entries[index][0][1]: entries[index][3]})
        return json.dumps(dict_list,indent=2)

class servers_state(socket_command):
    def jsonify(self):
        """Parse HAProxy servers state into JSON format"""
        lines = self.data[:-1]
        if lines == "Can't find backend.\n":
            return json.dumps(None, indent=2)
        lines = lines.splitlines()
        del lines[0]
        for index, line in enumerate(lines):
            lines[index] = lines[index].split(' ')
        del lines[0][0]
        dict_list = []
        for index in range(1,len(lines)):
            dict_list.append(dict(zip(lines[0],lines[index])))
        return json.dumps(dict_list,indent=2)
            
class pools(socket_command):
    def jsonify(self):
        """Parse HAProxy pools into JSON format"""
        lines = self.data[:-1]
        lines = lines.splitlines()
        del lines[0]
        total = lines.pop().split(' ')
        dict_list = []
        for index, line in enumerate(lines):
            line = lines[index].split(' ')
            dict_list.append({})
            dict_list[index]['name'] = line[4]
            dict_list[index]['bytes'] = line[5][1:]
            dict_list[index]['allocated'] = line[8]
            dict_list[index]['allocated bytes'] = line[10][1:]
            dict_list[index]['used'] = line[12]
            dict_list[index]['failure'] = line[14]
            dict_list[index]['users'] = line[16]
            if '[SHARED]' in line:
                dict_list[index]['shared'] = True
            else:
                dict_list[index]['shared'] = False
        pool_dict = {
            'pools'                 :dict_list,
            'total pools'           :total[1],
            'total bytes allocated' :total[3],
            'total bytes used'      :total[6]
        }
        return json.dumps(pool_dict, indent=2)

class table(socket_command):
    def jsonify(self):
        """Parse HAProxy table into JSON format"""
        lines = self.data[:-1].splitlines()
        dict_list = []
        for line in lines:
            line = line.split(' ')
            print(line)
            dict_list.append(dict([('table', line[2][:-1]),
                                   ('type' , line[4][:-1]),
                                   ('size' , line[5].split(':')[1][:-1]),
                                   ('used' , line[6].split(':')[1])]))
        return json.dumps(dict_list, indent=2)
        
#def parse_sess(data):
#    """Parse session information into JSON format"""
#    data = data[:-1]
#    entries = data.splitlines()
#    for index, entry in enumerate(entries):
#        entries[index] = entries[index].split(' ')
##  TODO: combine these two into a single func
#def parse_sess_id(data):
#    """Parse session information into JSON format"""
#    pass

class shut_frontend(socket_command):
    def jsonify(self):
        """Parse output of 'shutdown frontend' command into JSON format"""
        message = self.data[:-1]
        if message == 'Permission denied\n':
            r = {'status':'failed','code':'500','error':message[:-1]}
            return json.dumps(r, indent=2), 500
        elif message == 'No such frontend.\n':
            r = {'status':'failed','code':'404','error':message[:-1]}
            return json.dumps(r, indent=2), 404
        elif message == 'Frontend was already shut down.\n':
            r = {'status':'failed','code':'404','error':message[:-1]}
            return json.dumps(r, indent=2), 404
        elif message == 'A frontend name is expected.\n':
            r = {'status':'failed','code':'400','error':message[:-1]}
            return json.dumps(r, indent=2), 400
        elif message == '':
            r = {'status':'success','code':'200'}
            return json.dumps(r, indent=2), 200
        else:
            r = {'status':'unknown','code':'500'}
            return json.dumps(r, indent=2), 500

class shut_session(socket_command):
    def jsonify(self):
        """Parse output of 'shutdown session' command into JSON format"""
        message = self.data[:-1]
        if message == 'Permission denied\n':
            r = {'status':'failed','code':'500','error':message[:-1]}
            return json.dumps(r, indent=2), 500
        elif message == "No such session (use 'show sess').\n":
            r = {'status':'failed','code':'404','error':message[:-1]}
            return json.dumps(r, indent=2), 404
        elif message == "Session pointer expected (use 'show sess').\n":
            r = {'status':'failed','code':'400','error':message[:-1]}
            return json.dumps(r, indent=2), 400
        elif message == '':
            r = {'status':'success','code':'200'}
            return json.dumps(r, indent=2), 200
        else:
            r = {'status':'unknown','code':'500'}
            return json.dumps(r, indent=2), 500
