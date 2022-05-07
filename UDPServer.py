#from logging import exception, raiseExceptions
from pyexpat.errors import messages
import cv2, imutils, socket
import numpy as np
import time
import base64
import threading

BUFF_SIZE = 65536

CLIENT = []
USERS = {'user1':'1234', 'user2':'1234', 'user3':'1234', 'user4':'1234'}

def check_username(username):

    return  username in CLIENT.keys()

def full():

    if len(CLIENT) >=4:
        return True
    else:
        return False

def check_username(username):

    return  username in USERS.keys()

def check_password(username,password):

    return  password == USERS[username]
# Create a datagram socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '10.77.53.222' #socket.gethostbyname(host_name)
print(host_ip)
port = 9999
socket_address = (host_ip,port)

# Bind to address
server_socket.bind(socket_address)
print('Listening at:',socket_address)


vid = cv2.VideoCapture(0, cv2.CAP_DSHOW) #  replace 'rocket.mp4' with 0 for webcam


def receive():
    while True:
        msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('GOT connection from ',client_addr)
        msg=base64.b64decode(msg,' /').decode('ascii')
        
        msg = msg.split('::')

        if msg [0] == 'LOGIN':
            print('LOGIN')
            
            if not full():

                if check_username(msg[1]) :
                
                    if check_password(msg[1],msg[2]):      
                        text = "MESSAGE::AUTHORIZE"

                        server_socket.sendto(base64.b64encode(text.encode('ascii')),client_addr)
                        print('password match')
                        CLIENT.append(msg[1])
                        x = threading.Thread(target=streaming,args=(client_addr[0],client_addr[1],msg[1]))
                        x.start()
                    else:
                        text = "MESSAGE::UNAUTHORIZE"

                        server_socket.sendto(base64.b64encode(text.encode('ascii')),client_addr)
                        print("faild")
                        
                        
                        print('No')
            else:
                text = "MESSAGE::FULL"

                server_socket.sendto(base64.b64encode(text.encode('ascii')),client_addr)
                print("faild")

        elif msg[0] == 'QUIT':
            CLIENT.remove(msg[1])
            print(f'{msg[1]} quit the server')
      
        else :
            print('Wrong format of the packet received')


def streaming(client_addr1, e, username):
    client_adrr= (client_addr1,e)
    username = username
    WIDTH=400
    fps,st,frames_to_count,cnt = (0,0,20,0)
    while(vid.isOpened()):
               
        while username in CLIENT:
                    _,frame = vid.read()
                    frame = imutils.resize(frame,width=WIDTH)
                    encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                    
                    packet = 'VIDEO::'
                    for i in buffer:
                        packet += f'{i} '
            

                    message = base64.b64encode(packet.encode("ascii"))
                    server_socket.sendto(message,client_adrr)

        print(f'Stop broadcasting to {username}')
        break
            
receive()