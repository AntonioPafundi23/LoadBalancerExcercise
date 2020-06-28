import uuid

MAX_REQUESTS_CAPACITY = 10

class Provider:

	def __init__(self):
		self.unique_id = uuid.uuid4()
		self.is_alive = True
		
	def get_provider_id(self):
		return self.unique_id

	def check(self):
		return self.is_alive

	def turn_on(self):
		self.is_alive = True

	def turn_off(self):
		self.is_alive = False

	def get_max_request_capacity(self):
		return MAX_REQUESTS_CAPACITY

	def handle(self,client,request,load_balancer):
		response = f"this is a response of {self.unique_id} to client {client}"
		return response
