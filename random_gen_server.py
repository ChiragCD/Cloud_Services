import sys
import threading
import time
import random

from objects import Message

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
        self.address = "0.0.0.0:" + str(sys.argv[3])
        self.cloud_base_address = str(sys.argv[4])
        self.client_address = str(sys.argv[5])

        self.workers = dict()

    def add_worker(self, msg):

        worker = Worker()
        worker.id = msg.sender_id
        worker.address = msg.sender_address
        worker.healthy = 1
        worker.running = msg.status
        self.workers[worker.id] = worker
    
    def route_request(self, msg):

        available = [worker for worker in self.workers if self.workers[worker].running == 0 and self.workers[worker].healthy == 1]

        msg.sender_id = self.id
        if(not available):
            print("Dropping request")
            msg.type = "REQUEST_DROPPED"
            sendmsg(self.client_address, msg)
        decision = random.choice(available)
        msg.type = "USER_REQUEST"
        sendmsg(self.workersk[decision].address, msg)
    
    def route_reply(self, msg):

        msg.sender_id = self.id
        sendmsg(self.client_address, msg)
    
    def status_update(self, msg):

        sender = msg.sender_id

        if(sender not in self.workers):
            self.add_worker(msg)

        worker = self.workers[msg.sender_id]
        if(msg.type == "WORKER_HEALTH_UPDATE"):
            worker.health = msg.status
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
                    self.workers[worker].health = 0

            healthy_workers = [worker for worker in self.workers if self.workers[worker].healthy == 1]
            msg = Message()
            msg.sender_id = self.id
            msg.type = "PROCESS_HEALTH_UPDATE"
            msg.data = "Service " + str(self.family_id) + " has " + str(len(healthy_workers)) + " healthy processes out of " + str(len(list(self.workers)))
            sendmsg(self.clientaddress, msg)
    
    def scale(self):

        while(self.active):
            time.sleep(1)
            running = [worker for worker in self.workers if self.workers[worker].running == 1]

            msg = Message()
            msg.sender_id = self.id
            msg.type = "SCALING_DATA"
            msg.data = str(self.family_id) + " " + str(len(running)) + " " + str(len(self.workers))
            sendmsg(self.cloud_base_address, msg)
    
    
    def run(self):
        localIP     = "127.0.0.1"
        localPort   = 20001 #can be random but would be really convenient if we could just keep it same for all apps
        bufferSize  = 1024

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))


        while(True):
            bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)
            message = bytesAddressPair[0] #contains string form of object
            address = bytesAddressPair[1] #contains address of sender
            msg_obj = pickle.loads(message)
            msg_obj.sender_address = bytesAddressPair[0] + ':' + str(bytesAddressPair[1])

            if(msg_obj.type == "CLIENT_QUERY"):
                self.route_request(msg_obj)
            elif(msg_obj.type == "WORKER_REPLY"):
                self.route_reply(msg_obj)
            elif(msg_obj.type == "ADD_WORKER"): #idk what else to put here
                self.add_worker(msg_obj)
            else:
                self.status_update(msg_obj)

    def sendmsg(address, msg):
        serial_msg = pickle.dumps(msg)
        address_tuple = (adddress.split(":")[0], int(address.split(":")[1]))
        UDPServerSocket.sendto(address_tuple, serial_msg)

if(__name__ == "__main__"):
    server = RandomGenServer()
    monitor_thread = threading.Thread(target=server.monitor)
    scaling_thread = threading.Thread(target=server.scale)
    main_thread = threading.Thread(target=server.run)
    monitor_thread.start()
    scaling_thread.start()
    main_thread.start()