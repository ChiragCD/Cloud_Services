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

        pass

    def infrastructure_monitor(self, msg):

        pass

    def run(self):

        pass

if(__name__ == "__main__"):
    cloud_base = Server()
    cloud_base.run()