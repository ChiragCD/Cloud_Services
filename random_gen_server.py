import sys
import threading
import time
import random
import socket
import pickle

class Message(object):

    def __init__(self) -> None:
        super().__init__()

        self.sender_address = "0.0.0.0:0"
        self.receiver_address = "0.0.0.0:0"
        self.type = "NOT_INITIALIZED"
        self.sender_id = -1
        self.status = -1
        self.address = "0.0.0.0:0"
        self.container_action = -1
        self.container_type = -1
        self.process_family_identity = -1
        self.process_dest_identity = -1
        self.container_dest_identity = -1
        self.data = "Hehehe"

class Worker(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.address = "0.0.0.0:0"
        self.healthy = -1
        self.running = -1
        self.last_timestamp = time.time()

class RandomGenServer(object):

    def __init__(self) -> None:
        super().__init__()

        self.active = 1

        self.id = int(sys.argv[1])
        self.family_id = int(sys.argv[2])
        self.address = str(sys.argv[3])
        self.cloud_base_address = str(sys.argv[4])
        self.client_address = str(sys.argv[5])

        self.workers = dict()

        localIP     = self.address.split(":")[0]
        localPort   = int(self.address.split(":")[1]) #can be random but would be really convenient if we could just keep it same for all apps
        self.bufferSize  = 1024

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))

    def add_worker(self, msg):

        print("ADDING A WORKER")

        worker = Worker()
        worker.id = msg.sender_id
        worker.address = msg.sender_address
        worker.healthy = msg.status
        worker.running = 0
        self.workers[worker.id] = worker
    
    def route_request(self, msg):

        available = [worker for worker in self.workers if self.workers[worker].running == 0 and self.workers[worker].healthy == 1]
        print(self.workers[list(self.workers.keys())[0]].__dict__)
        print(available)

        msg.sender_id = self.id
        if(not available):
            print("Dropping request")
            msg.type = "REQUEST_DROPPED"
            self.sendmsg(self.client_address, msg)
            return
        decision = random.choice(available)
        msg.type = "USER_REQUEST"
        self.sendmsg(self.workers[decision].address, msg)
    
    def route_reply(self, msg):

        msg.sender_id = self.id
        self.sendmsg(self.client_address, msg)
    
    def status_update(self, msg):

        sender = msg.sender_id

        if(sender not in self.workers):
            self.add_worker(msg)

        worker = self.workers[msg.sender_id]
        if(msg.type == "WORKER_HEALTH_UPDATE"):
            worker.healthy = msg.status
        if(msg.type == "WORKER_ACTIVITY_UPDATE"):
            worker.running = msg.status

        worker.address = msg.sender_address
        worker.last_timestamp = time.time()
    
    def monitor(self):

        while(self.active):
            time.sleep(1)
            
            current_time = time.time()
            for worker in self.workers:
                if(current_time - self.workers[worker].last_timestamp > 2):
                    self.workers[worker].healthy = 0

            healthy_workers = [worker for worker in self.workers if self.workers[worker].healthy == 1]
            msg = Message()
            msg.sender_id = self.id
            msg.type = "PROCESS_HEALTH_UPDATE"
            msg.data = "Service " + str(self.family_id) + " has " + str(len(healthy_workers)) + " healthy processes out of " + str(len(list(self.workers)))
            self.sendmsg(self.client_address, msg)
    
    def scale(self):

        while(self.active):
            time.sleep(1)
            running = [worker for worker in self.workers if self.workers[worker].running == 1]

            msg = Message()
            msg.sender_id = self.id
            msg.type = "SCALING_DATA"
            msg.data = str(self.family_id) + " " + str(len(running)) + " " + str(len(self.workers))
            self.sendmsg(self.cloud_base_address, msg)
    
    
    def run(self):


        while(True):
            print("about to read a message")
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            print("just read a message")
            message = bytesAddressPair[0] #contains string form of object
            address = bytesAddressPair[1] #contains address of sender
            msg_obj = pickle.loads(message)
            msg_obj.sender_address = bytesAddressPair[1][0] + ":" + str(bytesAddressPair[1][1])

            print(msg_obj.type)

            if(msg_obj.type == "CLIENT_REQUEST"):
                self.route_request(msg_obj)
            elif(msg_obj.type == "WORKER_REPLY"):
                self.route_reply(msg_obj)
            elif(msg_obj.type == "WORKER_HEALTH_UPDATE" or msg_obj.type == "WORKER_ACTIVITY_UPDATE" ):
                self.status_update(msg_obj)

    def sendmsg(self, address, msg):
        serial_msg = pickle.dumps(msg)
        print(address)
        address_tuple = (address.split(":")[0], int(address.split(":")[1]))
        print(str(address_tuple))
        self.UDPServerSocket.sendto(serial_msg, address_tuple)

if(__name__ == "__main__"):
    server = RandomGenServer()
    monitor_thread = threading.Thread(target=server.monitor)
    scaling_thread = threading.Thread(target=server.scale)
    main_thread = threading.Thread(target=server.run)
    monitor_thread.start()
    scaling_thread.start()
    main_thread.start()