import time
import threading
import socket
import select
import errno
import sys
import datetime

list_ip = ["10.70.6.136", "192.168.100.92"]
list_port = [1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035,
             1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047,
             1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059,
             1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071,
             1072, 1073, 1074, 1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083,
             1084, 1085, 1086, 1087, 1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095,
             1096, 1097, 1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107,
             1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119,
             1120, 1121, 1122, 1123]
router_initial = [
{
  "router-name": "A",
  "server-port": 1024,
  "con-network": ["192.168.4.0/24", "192.168.1.0/24"]
},
{
  "router-name": "B",
  "server-port": 1025,
  "con-network": ["192.168.2.0/24"]
},
{
  "router-name": "D",
  "server-port": 1026,
  "con-network": ["192.168.4.0/24"]
},
{
  "router-name": "E",
  "server-port": 1027,
  "con-network": ["192.168.6.0/24"]
},
{
  "router-name": "F",
  "server-port": 1028,
  "con-network": ["192.168.5.0/24"]
},
{
  "router-name": "C",
  "server-port": 1029,
  "con-network": ["192.168.2.0/24", "192.168.3.0/24"]
}
]
clients = {}
routing_table = []
routing_msg = ""
def print_routing():
    print("|  Dest. Subnet  |   Next hop   |     Cost     |")
    print("------------------------------------------------")
    for i in range(len(routing_table)):
        print("|", routing_table[i][0], "|      ", routing_table[i][1], "     |      ", routing_table[i][2], "     |")

def server_process (IP, PORT):
    HEADER_LENGTH = 10

    #IP = "127.0.0.1"
    #PORT = 1234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    sockets_list = [server_socket]
    global clients
    global routing_msg
    print(f'Listening for connections on {IP}:{PORT}...')

    def receive_message(client_socket):

        try:

            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:
            return False

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))
                print("sockets list\n", sockets_list)
                print("clients\n", clients)
                print_routing()
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                user = clients[notified_socket]
                #print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')
                message_rcv = message["data"].decode("utf-8").split(":")
                if message_rcv[0] != "Hello":
                    break
                else:
                    print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

                for client_socket in clients:
                    if client_socket != notified_socket:
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]

def client_process (IP, PORT, user_name):
    global routing_msg
    HEADER_LENGTH = 10
    my_username = user_name
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    username = my_username.encode('utf-8')
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + username)

    while True:
        message = "Hello"
        if message:
            message = message + ":time>" + str(time.strftime("%H:%M:%S", time.gmtime(time.time()))) #str(datetime.timedelta(seconds = time.time()))
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            time.sleep(10)
            try:
                client_socket.send(message_header + message)
            except IOError as e:
                print('Reading error: {}'.format(str(e)))

        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print('Connection closed by the server')
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = client_socket.recv(username_length).decode('utf-8')
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')
                print(f'{username} > {message}')

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

def main():

    x = []
    router = []
    numServer = 1
    router_name = ""
    global routing_table
    global routing_msg
    print("Initial Router (Server)\n")
    if (int(numServer) != 0):
        for i in range(int(numServer)):
            indexIP = input("Index of IP (0 = intra, 1 = inter): ")
            indexRouter = input("Index of Router: ")
            router = router_initial[int(indexRouter)]
            router_name = str(router["router-name"])
            server_port = int(router["server-port"])

            for j in range(len(router["con-network"])):
                routing_table.append([router["con-network"][j], "-", "1"])
                if j == (len(router["con-network"]))-1:
                    routing_msg += router["con-network"][j] + "|-|1"
                else:
                    routing_msg += router["con-network"][j] + "|-|1:"

            print(routing_table)
            print(routing_msg)
            print("Server: ", router_name, " > ", list_ip[int(indexIP)], " port: ", server_port)
            thread = threading.Thread(target=server_process, args=(list_ip[int(indexIP)], server_port))
            x.append(thread)

    numClient = input("Number of Client: ")
    if (int(numClient) != 0):
        for i in range(int(numClient)):
            indexIP = input("Index of IP: ")
            indexPort = input("Index of Port: ")
            print("Client", i+1, list_ip[int(indexIP)], ":", list_port[(int(indexPort))])
            thread = threading.Thread(target=client_process, args=(list_ip[int(indexIP)], list_port[(int(indexPort))], router_name))
            x.append(thread)

    print(clients)
    for i in range((int(numClient)+int(numServer))):
        x[i].start()

if __name__=="__main__":
	main()
