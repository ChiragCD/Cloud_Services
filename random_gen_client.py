import socket
import pickle
import threading

from objects import Message

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", 4875))

def send_req():
    udp_socket.send()

def read():
    while(True):
        bytesAddressPair = udp_socket.recvfrom(1024)
        message = bytesAddressPair[0] #contains string form of object
        address = bytesAddressPair[1] #contains address of sender
        msg_obj = pickle.loads(message)
        msg_obj.sender_address = bytesAddressPair[1][0] + ':' + str(bytesAddressPair[1][1])
        print(msg_obj.type)
        print(msg_obj.data)

reader = threading.Thread(target=read)
reader.start()

def sendmsg(address, msg):
    serial_msg = pickle.dumps(msg)
    address_tuple = (address.split(":")[0], int(address.split(":")[1]))
    udp_socket.sendto(serial_msg, address_tuple)

while(True):
    choice = input()
    if(choice.upper() == "Y"):
        print("Sending")
        msg = Message()
        msg.type = "CLIENT_REQUEST"
        other_address = "172.17.62.78:6346"
        sendmsg(other_address, msg)
    else:
        break