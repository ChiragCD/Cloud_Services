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

class Machine(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.num_containers = 0
        self.containers = []
        self.health = -1
        self.address = "0.0.0.0:0"

class Container(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.health = -1

class Service(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.type = -1
        self.master_container_id = -1
        self.worker_container_ids = []
        self.master_process_id = -1
        self.worker_process_ids = []
        self.client_address = "0.0.0.0:0"

class Process(object):

    def __init__(self) -> None:
        super().__init__()

        self.id = -1
        self.type = -1
        self.status = -1
        self.health = -1
        self.family_id = -1
        self.address = "0.0.0.0:0"