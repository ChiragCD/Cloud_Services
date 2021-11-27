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
            ## sendmsg(msg, client)
        decision = random.choice(available)
        msg.type = "USER_REQUEST"
        ## sendmsg(decision, msg)
    
    def route_reply(self, msg):

        msg.sender_id = self.id
        ## sendmsg(client)
        pass
    
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
            # sendmsg(msg, clientaddress)
    
    def scale(self):

        while(self.active):
            time.sleep(1)
            running = [worker for worker in self.workers if self.workers[worker].running == 1]

            msg = Message()
            msg.sender_id = self.id
            msg.type = "SCALING_DATA"
            msg.data = str(self.family_id) + " " + str(len(running)) + " " + str(len(self.workers))
            # sendmsg(msg, cloudbase)
    
    def run(self):

        pass

if(__name__ == "__main__"):
    server = RandomGenServer()
    monitor_thread = threading.Thread(target=server.monitor)
    scaling_thread = threading.Thread(target=server.scale)
    main_thread = threading.Thread(target=server.run)
    monitor_thread.start()
    scaling_thread.start()
    main_thread.start()