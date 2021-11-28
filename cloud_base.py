from objects import *
import socket
import pickle
import threading
import time

class Server(object):

    def __init__(self) -> None:
        super().__init__()

        self.entities = dict()
        self.id = 1
        self.entities[1] = self

        self.machines = []
        self.containers = []
        self.platform_timestamps = dict()
        self.infrastructure_timestamps = dict()
    
    def start_service(self, msg):

        pass

    def scaler(self):

        pass

    def distributer(self):

        pass

    def scaling_wrapper(self, msg):

        pass

    def platform_update(self, msg):

        sender = msg.sender_id

        if(sender not in self.entities):
            container = Container()
            container.id = msg.sender_id
            self.entities[sender] = container
            self.containers.append(container)

        if(type(self.entities[sender] == Container)):
            self.entities[sender].health = msg.status
            self.platform_timestamps[sender] = time.time()

    def platform_monitor(self):

        while(True):
            time.sleep(1)

            current_time = time.time()
            for container in self.containers:
                if(current_time - self.platform_timestamps[container.id] > 2):
                    container.health = 0

            healthy = 0
            for container in self.containers:
                healthy += container.health
            print(healthy, "healthy containers out of", len(self.containers))

    def infrastructure_update(self, msg):

        sender = msg.sender_id

        if(sender not in self.entities):
            machine = Machine()
            machine.id = msg.sender_id
            machine.address = msg.sender_address
            self.entities[sender] = machine
            self.machines.append(machine)

        sender = msg.sender_id
        if(type(self.entities[sender] == Machine)):
            self.entities[sender].health = msg.status
            self.infrastructure_timestamps[sender] = time.time()

    def infrastructure_monitor(self):

        while(True):
            time.sleep(1)

            current_time = time.time()
            for machine in self.machines:
                if(current_time - self.infrastructure_timestamps[machine.id] > 2):
                    machine.health = 0

            healthy = 0
            for machine in self.machines:
                healthy += machine.health
            print(healthy, "healthy machines out of", len(self.machines))

    def sendmsg(self, address, msg):

        serial_msg = pickle.dumps(msg)
        address_tuple = (address.split(":")[0], int(address.split(":")[1]))
        self.UDPServerSocket.sendto(address_tuple, serial_msg)

    def run(self):

        ## convert udp message to Message object before passing to functions
        localIP     = "0.0.0.0"
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
            msg_obj.sender_address = bytesAddressPair[1][0] + ':' + str(bytesAddressPair[1][1])

            if(msg_obj.type == "START_SERVICE"):
                self.start_service(msg_obj)
            elif(msg_obj.type == "SCALING_DATA"): #idk what else to put here
                self.scaling_wrapper(msg_obj)
            elif(msg_obj.type == "CONTAINER_HEALTH_UPDATE"):
                self.platform_update(msg_obj)
            elif(msg_obj.type == "MACHINE_HEALTH_UPDATE"):
                self.infrastructure_update(msg_obj)
            else:
                print("ERROR DO NOT RECOGNIZE TYPE:"+ msg_obj.type)
        pass

if(__name__ == "__main__"):

    cloud_base = Server()
    main_thread = threading.Thread(target=cloud_base.run)
    infrastructure_monitor_thread = threading.Thread(target=cloud_base.infrastructure_monitor)
    platform_monitor_thread = threading.Thread(target=cloud_base.platform_monitor)

    main_thread.start()
    infrastructure_monitor_thread.start()
    platform_monitor_thread.start()