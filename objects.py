class Message(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.type = -1
        self.sender_id = -1
        self.status = -1
        self.address = "0.0.0.0:0"
        self.container_action = -1
        self.container_type = -1
        self.container_family_identity = -1
        self.container_dest_identity = -1
        self.data = "Hehehe"

class Machine(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.num_containers = 0
        self.containers = []
        self.status = -1
        self.address = "0.0.0.0:0"

class Container(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.status = -1
        self.type = -1
        self.health = -1
        self.address = "0.0.0.0:0"
        self.family_id = -1

class Service(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.type = -1
        self.master_node_id = -1
        self.worker_node_ids = []
        self.client_address = "0.0.0.0:0"