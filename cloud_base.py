from objects import *

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
        self.containers = []
    
    def start_service(self, msg):

        pass

    def update_client(self, msg):

        pass

    def update_master_node(self, msg):

        pass

    def scaler(self):

        pass

    def distributer(self):

        pass

    def scaling_wrapper(self, msg):

        pass

    def platform_monitor(self, msg):

        sender = msg.sender_id
        if(msg.type == "CONTAINER_HEALTH_UPDATE" and type(self.entities[sender] == Container)):
            self.entities[sender].health = msg.status

        healthy = 0
        for container in self.containers:
            healthy += container.health
        print(healthy, "healthy containers out of", len(self.containers))

    def infrastructure_monitor(self, msg):

        sender = msg.sender_id
        if(msg.type == "MACHINE_HEALTH_UPDATE" and type(self.entities[sender] == Machine)):
            self.entities[sender].status = msg.status

        healthy = 0
        for machine in self.machines:
            healthy += machine.status
        print(healthy, "healthy machines out of", len(self.machines))
    
    def general_update(self, msg):

        sender = msg.sender_id

        if(sender not in self.entities):
            if(msg.type == "CONTAINER_GENERAL_UPDATE"):
                container = Container()
                self.entities[sender] = container
                self.containers.append(container)

        if(msg.type == "CONTAINER_GENERAL_UPDATE" and type(self.entities[sender]) == Container):
            self.entities[sender].address = msg.sender_address
            self.entities[sender].status = msg.status
            self.entities[sender].health = 1
            self.entities[sender].family_id = msg.container_family_identity

        ## MACHINE_GENERAL_UPDATE - Optional

        if(sender not in self.entities):
            if(msg.type == "MACHINE_GENERAL_UPDATE"):
                machine = Machine()
                machine_id = len(self.machines) + 1 + 10
                machine.address = msg.ssender_address
                machine.id = machine_id
                self.entities[sender] = machine
                self.machines.append(machine)
                ## TODO - sendmsg("""Give machine the new sender_id""")

        if(msg.type == "MACHINE_GENERAL_UPDATE" and type(self.entities[sender]) == Machine):
            self.entities[sender].address = msg.sender_address
            self.entities[sender].status = msg.status
            ## TODO - Other Data

    def run(self):

        ## convert udp message to Message object before passing to functions
        pass

if(__name__ == "__main__"):
    cloud_base = Server()
    cloud_base.run()