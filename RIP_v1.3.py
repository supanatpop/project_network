import time
import threading
import socket
import select
import errno
import sys
import datetime

hostname = socket.gethostname()
IP_host = socket.gethostbyname(hostname)
print("My IP Address:" + IP_host)
list_ip = [str(IP_host), "192.168.100.92"]
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
        "con-network": ["192.168.1.0/24", "192.168.4.0/24"]
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
router_name = ""
sockets_list = []
arr_client = []


def print_routing():
    print("|  Dest. Subnet  |   Next hop   |     Cost     |")
    print("------------------------------------------------")
    for i in range(len(routing_table)):
        print("|", routing_table[i][0], "|      ", routing_table[i][1], "     |      ", routing_table[i][2], "     |")


def update_routing(message, user):
    global routing_msg
    global routing_table

    for i in range(int(len(message)) - 1):
        arr = message[(i + 1)].split("|")
        count = 0
        for j in range(len(routing_table)):
            if routing_table[j][0] != arr[0]:
                count += 1
            elif (routing_table[j][0] == arr[0]) & (int(routing_table[j][2]) > (int(arr[2]) + 1)):
                routing_table[j][1] = str(user)
                routing_table[j][2] = str(int(arr[2]) + 1)
            if count == len(routing_table):
                routing_table.append([str(arr[0]), str(user), str(int(arr[2]) + 1)])

    routing_msg = ""
    for i in range(len(routing_table)):
        if i == (len(routing_table)) - 1:
            routing_msg += routing_table[i][0] + "|" + routing_table[i][1] + "|" + routing_table[i][2]
        else:
            routing_msg += routing_table[i][0] + "|" + routing_table[i][1] + "|" + routing_table[i][2] + ":"
    print(routing_msg)


def send_routing(message):
    global clients
    global arr_client
    arr_socket = list(clients.keys())
    for socket_client in arr_socket:
        socket_client.send(message.encode())
    arr_client = list(clients.values())


def edit_routing():
    global arr_client
    global routing_table
    global routing_msg
    global router_name
    global clients
    arr = list(clients.values())
    node = set(arr_client).symmetric_difference(set(arr))
    #print(len(arr))
    #print(arr)
    #print(routing_table)
    tmp = []
    count = 0
    for i in range(len(routing_table)):
        for j in range(len(arr)):
            arr_split = arr[j].split(":")
            if (routing_table[i][1] != arr_split[0]) and (routing_table[i][1] != "-"):
                tmp.append(i)
    #print(tmp)
    count = 0
    for i in tmp:
        if count == 0:
            #print(i)
            del routing_table[i]
            count += 1
        elif (count > 0) and (count < len(tmp)):
            #print(i - count)
            routing_table.remove(routing_table[(i-count)])
            count += 1

    arr_client = arr
    routing_msg = ""
    for l in range(len(routing_table)):
        if l == (len(routing_table)) - 1:
            routing_msg += routing_table[l][0] + "|" + routing_table[l][1] + "|" + routing_table[l][2]
        else:
            routing_msg += routing_table[l][0] + "|" + routing_table[l][1] + "|" + routing_table[l][2] + ":"
    print_routing()
    #print(clients, arr_client, routing_msg)
    if len(clients) != 0:
        msg_rt = str(router_name + ":" + routing_msg)
        send_routing(msg_rt)



def server_process(IP, PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    global clients
    global routing_msg
    global router_name
    global sockets_list
    global arr_client
    sockets_list = [server_socket]

    print(f'Listening for connections on {IP}:{PORT}...')

    def receive_message(client_socket):

        try:
            message = client_socket.recv(2048)

            if not len(message):
                return False

            return message.decode('utf-8')

        except:
            return False

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                message = receive_message(client_socket)
                if message is False:
                    continue
                message_split = message.split(":")
                sockets_list.append(client_socket)
                clients[client_socket] = message_split[0]
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, message_split[0]))
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    edit_routing()
                    continue
                user = clients[notified_socket]
                message_rcv = message.split(":")
                if (message_rcv[0] == "RoutingTable") | (message_rcv[0] in arr_client) | (message_rcv[0] == "Hello"):
                    print(f'Received message from {user}: {message}')
                    update_routing(message_rcv, user)
                    print_routing()
                    msg_rt = str(router_name + ":" + routing_msg)
                    send_routing(msg_rt)

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
            edit_routing()


def client_process(IP, PORT, user_name):
    time_send = 0
    global routing_msg
    global arr_client
    global clients
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    clients[client_socket] = user_name  # ADD
    client_socket.setblocking(False)
    user_name = str(user_name + ":")
    client_socket.send(user_name.encode('utf-8'))
    time.sleep(1)
    message = "RoutingTable:" + routing_msg
    client_socket.send(message.encode('utf-8'))
    clients[client_socket] = user_name

    while True:

        time.sleep(time_send)

        message = ""
        message = "RoutingTable:" + routing_msg
        if message:
            #message = message + ":time>" + str(time.strftime("%H:%M:%S", time.gmtime(time.time())))
            
            #time.sleep(5)
            
            try:
                client_socket.send(message.encode('utf-8'))
                #status = False
            except IOError as e:
                print('Reading error (Client-Send): {}'.format(str(e)))
                edit_routing()
        try:
            while True:
                message = client_socket.recv(2048).decode('utf-8')
                message_split = message.split(":")
                update_routing(message_split, message_split[0])
                print_routing()

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error IOError (Client-Receive): {}'.format(str(e)))
                time_send = time_send+2
                #sys.exit()
            continue

        except Exception as ee:
            print('exception')
            print(format(str(ee)))
            time_send = time_send+5
            #sys.exit()


def main():
    x = []
    router = []
    numServer = 1
    global router_name
    global routing_table
    global routing_msg
    print("Initial Router (Server)\n")
    if (int(numServer) != 0):
        for i in range(int(numServer)):
            indexRouter = input("Index of Router: ")
            router = router_initial[int(indexRouter)]
            router_name = str(router["router-name"])
            server_port = int(router["server-port"])

            for j in range(len(router["con-network"])):
                routing_table.append([router["con-network"][j], "-", "1"])
                if j == (len(router["con-network"])) - 1:
                    routing_msg += router["con-network"][j] + "|-|1"
                else:
                    routing_msg += router["con-network"][j] + "|-|1:"

            print(routing_table)
            print(routing_msg)
            print("Server: ", router_name, " > ", list_ip[0], " port: ", server_port)
            thread = threading.Thread(target=server_process, args=(list_ip[0], server_port))
            x.append(thread)


    numClient = input("Number of Client: ")
    if (int(numClient) != 0):
        for i in range(int(numClient)):
            indexIP = input("Type of Network (0 = internal, 1 = external): ")
            while not int(indexIP) in range(0, 2):
                indexIP = input("Type of Network (0 = internal, 1 = external): ")
            indexPort = input("Index of Port: ")
            while not int(indexPort) in range(0, 100):
                indexPort = input("Index of Port: ")
            print("Client", i + 1, "Connect to ", list_ip[int(indexIP)], ":", list_port[(int(indexPort))], "\n")
            thread = threading.Thread(target=client_process,
                                      args=(list_ip[int(indexIP)], list_port[(int(indexPort))], router_name))
            x.append(thread)

    for i in range((int(numClient) + int(numServer))):
        x[i].start()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
