from objects import *
import socket
import pickle
import threading
import time
import sys

class Server(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = sys.argv[1]
        self.address = sys.argv[2]
        self.cloud_base_address = sys.argv[3]

        self.containers = dict()

        ## convert udp message to Message object before passing to functions
        localIP     = self.address.split(":")[0]
        localPort   = int(self.address.split(":")[1])
        self.bufferSize  = 1024

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))

        print("UDP server up and listening")

    def add_container(self, msg):

        pass

    def remove_container(self, msg):

        pass

    def send_migration(self, msg):

        pass

    def receive_migration(self, msg):

        pass

    def platform_heartbeat(self):

        while(True):
            time.sleep(1)

            for container_id in self.containers:
                if(self.containers[container_id].health == 0):
                    pass
                msg = Message()
                msg.type = "CONTAINER_HEALTH_UPDATE"
                msg.sender_id = container_id
                msg.status = 1
                self.sendmsg(self.cloud_base_address, msg)

    def infrastructure_heartbeat(self):

        while(True):
            time.sleep(1)

            msg = Message()
            msg.type = "MACHINE_HEALTH_UPDATE"
            msg.sender_id = self.id
            msg.status = 1
            self.sendmsg(self.cloud_base_address, msg)

    def sendmsg(self, address, msg):
        
        serial_msg = pickle.dumps(msg)
        address_tuple = (address.split(":")[0], int(address.split(":")[1]))
        self.UDPServerSocket.sendto(serial_msg, address_tuple)

    def run(self):

        while(True):

            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0] #contains string form of object
            address = bytesAddressPair[1] #contains address of sender
            msg_obj = pickle.loads(message)
            msg_obj.sender_address = bytesAddressPair[0] + ':' + str(bytesAddressPair[1])

            if(msg_obj.type == "ADD_CONTAINER"):
                self.add_container(msg_obj)
            elif(msg_obj.type == "REMOVE_CONTAINER"): #idk what else to put here
                self.remove_container(msg_obj)
            elif(msg_obj.type == "SEND_MIGRATION"):
                self.send_migration(msg_obj)
            elif(msg_obj.type == "RECEIVE_MIGRATION"):
                self.receive_migration(msg_obj)
            else:
                print("ERROR DO NOT RECOGNIZE TYPE:"+ msg_obj.type)

if(__name__ == "__main__"):

    machine_base = Server()
    main_thread = threading.Thread(target=machine_base.run)
    infrastructure_heartbeat_thread = threading.Thread(target=machine_base.infrastructure_heartbeat)
    platform_heartbeat_thread = threading.Thread(target=machine_base.platform_heartbeat)

    main_thread.start()
    infrastructure_heartbeat_thread.start()
    platform_heartbeat_thread.start()