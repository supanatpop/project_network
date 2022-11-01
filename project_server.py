import socket
import threading
import errno




def check_port_server(ip_client, port_client):
    try:
        serversocker.bind((ip_client, port_client))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return False
    return True


def add_name_local(client,ip_client_add,port_client_add,link_cost_add):
    active_clients[client] = {'name' : client,'ip_client' :ip_client_add,'port_client' : port_client_add,'link_cost_client' : link_cost_add}

    add_connent_router(client)



def send_msg(msg,ip_server_send,port_server_send):
    msg = msg.encode('utf-8')
    serversocker.sendto(msg,(ip_server_send,port_server_send))




def remove_user(key_remove):
    active_clients.pop(key_remove,None)


def recieve():
    
    while 1:
        x = serversocker.recvfrom(2048)

        #rec_ip = x[1][0]
        rec_port = x [1][1]
        message = x[0].decode('utf-8')


        parts = message.split(',')
        print(f' print_split {parts} \n')
        match parts[0]:
            case 'start':
                if not parts[1] in active_clients:
                    # ชื่อเครื่อง , ip เครื่อง client , port client , link cost
                    #active_clients[parts[1]] = {'name' : parts[1],'ip_client' :parts[2],'port_client' : rec_port,'lonk_cost_client' : parts[3]}

                    add_name_local(parts[1],parts[2],rec_port,parts[3])


                    msg = 'start,'+name_client+','+ip_client+','+str(link_cost)

                    send_msg(msg,parts[2],rec_port)#function

                    add_connent_router(parts[1])#function


                    #แก้เพราะเวลาเปิดเครื่อง 1 port 1000 พอเปิดเครื่อง 2 port 1001 เครื่องที่ 2 ส่ง 1 ได้
                    # พอเปิดเครื่องที่ 3 port 1003 ส่ง 2 ได้ แต่ส่งไปหาเครื่องที่ 1 ไม่ได้
                                    

                    #active_clients['b'] ={'k1' : 'b1', 'k2' :'b2v'}
                else:
                    add_name_local(parts[1],parts[2],rec_port,parts[3])


            case 'update link cost':
                active_clients[parts[1]]['link_cost_client'] = parts[2]
            case _:
                print("Code not found")




def add_connent_router(name_router):
    
    if not name_router in connent_router:
        connent_router.append(name_router)


def send_messages_start():
    
    add_name_local(name_client,ip_client,port_client,link_cost)

    msg = 'start,'+name_client+','+ip_client+','+str(link_cost)
    print(msg)

    send_msg(msg,ip_server,port_server)

        



def send_message_all(link_cost,active_clients):

    msg = 'update link cost,'+name_client+','+str(link_cost)
        
    
    for user in active_clients:
        if user != name_client:
            send_msg(msg,active_clients[user]['ip_client'],active_clients[user]['port_client'])
        #print(active_clients[user]['port_client'])

    #-----------------------------------------------------------------------
def show_table():
    print('ss')


try:
    active_clients  = {}
    link_cost = ''

    connent_router = []#เก็บชื่อ router ว่าเชื่อมต่อกับ router ไหน



    serversocker = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


    name_client = input('Enter name router: ')
    ip_client = input('Enter ip address build local: ')
    port_client = int(input('Enter port build local: '))

    

    if check_port_server(ip_client, port_client):
        print('Server OK')
    else:
        print('Port is already in use')
        exit()



    thread_recieve = threading.Thread(target=recieve).start()

    #connnent server
        
    ip_server = ''
    while ip_server != 'end':
            
        ip_server = input('Enter ip connent address Server: ')

        if ip_server == 'end' or ip_server == '':
            break
        else:
            port_server = int(input('Enter port connent number Server: '))

            link_cost = int(input('Enter link cost: '))

        send_messages_start()
    





    input_order = ''

        
    while 1:
        
        input_order = input('ใส่คำสั่ง :')

        if input_order == 'show':
            input_show = ''

            while input_show != 'end':
                input_show = input('Enter Show user: ')
                #print('connent router', connent_router)
                if input_show == 'all':
                    print('user ', active_clients)
                elif input_show == 'table':
                    show_table()
                else:
                    if input_show in active_clients:
                        print('user show'+input_show+': ',active_clients[input_show])
                    else:
                        print('ไม่มีข้อมูล')

        elif input_order == 'send':
            print(f'link cost old : {link_cost}')
            update_link_cost = input('Enter link cost: ')

            if update_link_cost != '':
                link_cost = int(update_link_cost)

            send_message_all(link_cost,active_clients)
        elif input_order == 'rm':
            key_remove = input('Enter remove user :')

            remove_user(key_remove)
        else:
            print('ไม่มีคำสั่ง')

except KeyboardInterrupt:
    exit()
