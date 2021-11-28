from objects import *
import socket
import pickle
import threading
import time

class Server(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = 1
        self.containers = dict()
    
    def start_service(self, msg):

        pass

    def update_client(self, msg):
        msg.address = msg.sender_address
        service = entities[entities[msg.sender_id].type] #not sure if this is correct
        client_address = service.client_address
        client_tuple = (client_address.split(":")[0],client_address.split(":")[1])
        msg.type = "SERVICE_UP"
        self.UDPServerSocket.sendto(msg,client_tuple)

    def update_master_node(self, msg):
        sender = msg.sender_id
        container = entities[sender] 
        ms_id = container.family_id
        ms_container = entities[ms_id]
        ms_address = ms_container.address
        ms_tuple = (ms_address.split(":")[0],ms_address.split(":")[1])
        msg.receiver_address = ms_address
        msg.type = "WORKER_UP"
        self.UDPServerSocket.sendto(msg, ms_tuple)

    def add_container(self):

        pass

    def remove_container(self):

        pass

    def platform_monitor(self):

        while(True):
            time.sleep(1)

            msg = Message()
            msg.type = "CONTAINER_HEALTH_UPDATE"
            msg.sender_id = self.id
            msg.status = 1
            self.sendmsg(self.main_server_address, msg)

    def infrastructure_heartbeat(self):

        while(True):
            time.sleep(1)

            msg = Message()
            msg.type = "MACHINE_HEALTH_UPDATE"
            msg.sender_id = self.id
            msg.status = 1
            self.sendmsg(self.main_server_address, msg)

    def sendmsg(self, address, msg):
        
        serial_msg = pickle.dumps(msg)
        address_tuple = (address.split(":")[0], int(address.split(":")[1]))
        self.UDPServerSocket.sendto(address_tuple, serial_msg)

    def run(self):

        ## convert udp message to Message object before passing to functions
        localIP     = "127.0.0.1"
        localPort   = 20001
        bufferSize  = 1024

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))

        print("UDP server up and listening")

        while(True):

            bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)
            message = bytesAddressPair[0] #contains string form of object
            address = bytesAddressPair[1] #contains address of sender
            msg_obj = pickle.loads(message)
            msg_obj.sender_address = bytesAddressPair[0] + ':' + str(bytesAddressPair[1])

            if(msg_obj.type == "START_SERVICE"):
                self.start_service(msg_obj)
            #elif(msg_obj.type == "UPDATE_CLIENT"):
            #    self.update_client(msg_obj)
            #elif(msg_obj.type == "UPDATE_MASTER_NODE"):
            #    self.update_master_node(msg_obj)
            elif(msg_obj.type == "SCALING_DATA"): #idk what else to put here
                self.scaling_wrapper(msg_obj)
            elif(msg_obj.type == "CONTAINER_HEALTH_UPDATE"):
                self.platform_update(msg_obj)
            elif(msg_obj.type == "MACHINE_HEALTH_UPDATE"):
                self.infrastructure_update(msg_obj)
            else:
                self.general_update(msg_obj)
        pass

if(__name__ == "__main__"):

    cloud_base = Server()
    main_thread = threading.Thread(target=cloud_base.run)
    infrastructure_monitor_thread = threading.Thread(target=cloud_base.infrastructure_monitor)
    platform_monitor_thread = threading.Thread(target=cloud_base.platform_monitor)

    main_thread.start()
    infrastructure_monitor_thread.start()
    platform_monitor_thread.start()