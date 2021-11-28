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
        self.Next_Service_id = 101
        self.Next_Process_id = 1001
        self.Next_msg_id = 10001

    def sendmsg(self, address, msg):
        
        serial_msg = pickle.dumps(msg)
        address_tuple = (address.split(":")[0], int(address.split(":")[1]))
        self.UDPServerSocket.sendto(address_tuple, serial_msg)
    
    def start_service(self, msg):
        # make service obj
        new_service = Service()
        new_service.id = self.Next_Service_id
        self.Next_Service_id += 1
        new_service.type = int(msg.data)
        self.distributer(self, new_service.id, 1, True)
        self.distributer(self, new_service.id, 2, False)

    def scaler(self, service_id):

        Threshold = 0.8
        Containers_up = 0
        Containers_busy = 0
        unused_workers = []
        Dict = {}
        itr = 0
        
        for worker_process in self.entities[service_id].worker_process_ids:
            if self.entities[worker_process].health == 0:
                Containers_up += 1
                unused_workers.append(worker_process)
                Dict[worker_process] = itr
            if self.entities[worker_process].health == 1:
                Containers_busy += 1
                Containers_up += 1
            itr += 1

        req = (Containers_busy-Threshold*Containers_up)/Threshold
        new_process_ids = []

        if req > 0:
            for x in range(req):
                new_process = Process()
                new_process.id = self.Next_Process_id
                # update the type of process
                self.entities[new_process.id] = new_process
                new_process_ids.append(new_process.id)
                self.Next_Process_id += 1
                self.entities[service_id].worker_process_ids.append(new_process.id)

        return req, new_process_ids

    def distributer(self, service_id, needed, new_process_ids, Master):

        if needed > 0:
            done = 0
            container_ids = []
            for machine in self.machines:
                for container in machine.containers:
                    if container.health == 0:
                        container_ids.append(container.id)
                        msg = Message()
                        msg.receiver_address = machine.address
                        msg.id = self.Next_msg_id
                        self.Next_msg_id += 1
                        if Master == True:
                            msg.type = "WAKE_UP_MASTER_NODE"
                        msg.status = 1
                        msg.conatiner_action = 1
                        msg.container_type = 1 # 1 for master and 2 for worker

                        done += 1
                    if done == needed:
                        break
                if done == needed:
                    break

        if needed < 0:

            pass

        # make container obj

    def scaling_wrapper(self, msg):

        Extra, new_process_ids = self.scaler(self.entities[msg.sender_id].family_id)
        self.distributer(self.entities[msg.sender_id].family_id, Extra, new_process_ids)

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