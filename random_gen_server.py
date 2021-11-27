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

class RandomGenServer(object):

    def __init__(self) -> None:
        super().__init__()

        self.active = 1

        self.id = int(sys.argv[1])
        self.family_id = int(sys.argv[2])
        self.address = "0.0.0.0:" + str(sys.argv[3])
        self.cloud_base_address = str(sys.argv[4])
        self.client_address = str(sys.argv[5])

        self.workers = []

    def add_worker(self, msg):

        worker = Worker()
        worker.id = msg.sender_id
        worker.address = msg.sender_address
        worker.id = msg.status
        self.workers.append(worker)

    def delete_worker(self, msg):

        worker = self.workers[int(msg.data)]
        worker.health = 0
        # sendmsg(worker)
    
    def route_request(self, msg):

        available = [worker for worker in self.workers if worker.running == 0 and worker.healthy == 1]
        if(not available):
            print("Dropping request")
            ## sendmsg(client)
        decision = random.choice(available)
        ## sendmsg(decision)
    
    def route_reply(self, msg):

        ## sendmsg(client)
        pass
    
    def status_update(self, msg):

        worker = self.workers[msg.sender_id]
        if(msg.type == "WORKER_HEALTH_UPDATE"):
            worker.health = msg.status
        if(msg.type == "WORKER_ACTIVITY_UPDATE"):
            worker.running = msg.status
        worker.address = msg.sender_address
    
    def monitor(self):

        while(self.active):
            time.sleep(1)
            healthy = [worker for worker in self.workers if worker.healthy == 1]

            msg = Message()
            msg.type = "PROCESS_HEALTH_UPDATE"
            msg.data = "Service " + str(self.family_id) + " has " + str(len(healthy)) + " healthy processes out of " + str(len(self.workers))
            # sendmsg(msg, clientaddress)
    
    def scale(self):

        while(self.active):
            time.sleep(1)
            running = [worker for worker in self.workers if worker.running == 1]

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