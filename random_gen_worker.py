import sys
import threading
import time
import random
import pickle
import socket

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

class RandomGenWorker(object):

    def __init__(self) -> None:
        super().__init__()

        self.active = 1

        self.id = int(sys.argv[1])
        self.family_id = int(sys.argv[2])
        self.address = str(sys.argv[3])
        self.main_server_address = str(sys.argv[4])

        localIP     = self.address.split(":")[0]
        localPort   = int(self.address.split(":")[1]) #can be random but would be really convenient if we could just keep it same for all apps
        self.bufferSize  = 1024

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))

    def handle_request(self, msg):
        print("Genning number")
        in_use_msg = Message()
        in_use_msg.sender_id = self.id
        in_use_msg.type = "WORKER_ACTIVITY_UPDATE"
        in_use_msg.receiver_address = self.main_server_address
        in_use_msg.status = 1
        self.sendmsg(self.main_server_address, in_use_msg)

        a = 0
        for i in range(100000):
            a = a+1

        answer = random.randint(0, 10000)

        answer_msg = Message()
        answer_msg.sender_id = self.id
        answer_msg.type = "WORKER_REPLY"
        answer_msg.receiver_address = self.main_server_address
        answer_msg.data = str(answer)
        self.sendmsg(self.main_server_address, answer_msg)

        done_msg = Message()
        done_msg.sender_id = self.id
        done_msg.type = "WORKER_ACTIVITY_UPDATE"
        done_msg.receiver_address = self.main_server_address
        done_msg.status = 0
        self.sendmsg(self.main_server_address, done_msg)
        pass

    def heartbeat(self):

        while(True):
            time.sleep(1)

            msg = Message()
            msg.type = "WORKER_HEALTH_UPDATE"
            msg.sender_id = self.id
            msg.status = 1
            self.sendmsg(self.main_server_address, msg)
    
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
            msg_obj.sender_address = bytesAddressPair[1][0] + ':' + str(bytesAddressPair[1][1])

            print(msg_obj.type)
            if(msg_obj.type == "USER_REQUEST"):
                self.handle_request(msg_obj)

        pass



if(__name__ == "__main__"):
    worker = RandomGenWorker()
    heartbeat_thread = threading.Thread(target=worker.heartbeat)
    main_thread = threading.Thread(target=worker.run)
    heartbeat_thread.start()
    main_thread.start()