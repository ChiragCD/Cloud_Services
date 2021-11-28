import socket
import pickle
import threading

from objects import Message

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", 4875))
cloud_base_address = "172.17.63.61:20001"

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

def start_service(choice):
    msg = Message()
    choice_dict = {1:"RANDOM_NUMBER_GENERATOR",2:"CLOUD_SEARCH",3:"S3"}
    msg.type = "START_SERVICE"
    msg.choice = choice_dict[choice]
    sendmsg(cloud_base_address, msg)

def send_query(data):
    msg = Message()
    msg.type = "CLIENT_REQUEST"
    msg.data = data
    sendmsg(cloud_base_address, msg)

def sendmsg(address, msg):
    serial_msg = pickle.dumps(msg)
    address_tuple = (address.split(":")[0], int(address.split(":")[1]))
    udp_socket.sendto(serial_msg, address_tuple)

while(True):
    choice = input("1. Random Number Generator\n2. Cloud Search\n3. Secure Storage Service (S3)")
    choice = int(choice)
    if(choice <=0 or choice > 3):
        continue
    start_service(choice)
    break

while(True):
    data = input("Enter the input you would like to give to the service")
    print("Sending")
    send_query(data)