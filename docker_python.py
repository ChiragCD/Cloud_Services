from typing import Container
import docker 
import socket
import pickle

from objects import Message


class DockerInterface(object):
	def __init__(self) -> None:
		super().__init__()
	
		self.script_images = ["random-docker"] #Add more docker images
		self.client = docker.from_env()
		self.container_id_map = dict()

	def spawn_container(self, msg):
		container = self.client.containers.create(self.script_images[msg.type])
		self.container_id_map[msg.id] = container.id
		
	def kill_container(self, msg):
		container = self.get(self.container_id_map[msg.id])
		container.stop()

	def run(self):

		localIP = "0.0.0.0"
		localPort = 20001
		bufferSize = 1024

		# self.spawn_container(self.message)
		self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
		self.UDPServerSocket.bind((localIP, localPort))

		print("UDP server up and listening")

		while(True):

			bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)
			message = bytesAddressPair[0] #contains string form of object
			address = bytesAddressPair[1] #contains address of sender
			msg_obj = pickle.loads(message)
			msg_obj.sender_address = bytesAddressPair[0] + ':' + str(bytesAddressPair[1])

			self.spawn_container(msg_obj)
	
	def sendmsg(address, msg):
		serial_msg = pickle.dumps(msg)
		address_tuple = (address.split(":")[0], int(address.split(":")[1]))
		UDPServerSocket.sendto(address_tuple, serial_msg)

if(__name__ == "__main__"):
	interface = DockerInterface()
	interface.run()
	print("Script Running")