from objects import *
import socket
import pickle

class Server(object):

    def __init__(self) -> None:
        super().__init__()

        self.entities = dict()
        self.id = 1
        self.entities[1] = self

        machine1 = Machine()
        machine1.id = 11
        self.entities[11] = machine1
        machine1.address = "0.0.0.0:0"

        machine2 = Machine()
        machine2.id = 12
        self.entities[12] = machine2
        machine2.address = "0.0.0.0:0"

        machine3 = Machine()
        machine3.id = 13
        self.entities[13] = machine3
        machine3.address = "0.0.0.0:0"

        self.machines = [machine1, machine2, machine3]
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
        Next_Service_id += 1
        new_service.type = int(msg.data)
        distributer(self, new_service.id, 1, True)
        distributer(self, new_service.id, 2, False)

    def update_client(self, msg):
        msg.address = msg.sender_address
        service = entities[entities[msg.sender_id].type] #not sure if this is correct
        client_address = service.client_address
        client_tuple = (client_address.split(":")[0], client_address.split(":")[1])
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
                        msg.receiver_address = machine.address
                        msg.id = self.Next_msg_id
                        Next_msg_id += 1
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

        # make container obj

    def scaling_wrapper(self, msg):

        Extra, new_process_ids = scaler(self.entities[msg.sender_id].family_id)
        distributer(self.entities[msg.sender_id].family_id, Extra, new_process_ids)

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
                self.`eral_update(msg_obj)
        pass

if(__name__ == "__main__"):

    cloud_base = Server()
    main_thread = threading.Thread(target=cloud_base.run)
    infrastructure_monitor_thread = threading.Thread(target=cloud_base.infrastructure_monitor)
    platform_monitor_thread = threading.Thread(target=cloud_base.platform_monitor)

    main_thread.start()
    infrastructure_monitor_thread.start()
    platform_monitor_thread.start()