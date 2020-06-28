import random
import threading
import time
from multiprocessing import Lock
import enum
from provider import Provider


MAX_NUMBER_REGISTERED_PROVIDERS = 10
TIME_CHECK_PROVIDER_ALIVE = 1 #sec
FREQ_TO_REINCLUDE_PROVIDER = 2 #sec

class LoadBalancerType(enum.Enum):
	ROUND_ROBIN = 0
	RANDOM = 1


class LoadBalancer():
	def __init__(self,load_balancer_type=LoadBalancerType.ROUND_ROBIN):
		self.list_of_provider_id = []
		self.id_to_provider = {}
		self.round_robin_index = 0
		self.map_freq_excluded_providers = {}
		self.load_balancer_type = load_balancer_type
		thread_check = threading.Thread(target=self.check_providers_alive)
		thread_check.daemon = True  # Explicitly set property.
		thread_check.start()
		self.lock = Lock()

	def check_providers_alive(self):
		starttime=time.time()
		while True:
			for idx,provider_id in enumerate(self.list_of_provider_id):
				provider = self.id_to_provider[provider_id]["provider"]
				if not provider.check():
					self.exclude_provider(provider_id)
					self.map_freq_excluded_providers[provider] = 0

			for excluded_provider, freq in self.map_freq_excluded_providers.items():
				if excluded_provider.check():
					freq+=1
					if freq == FREQ_TO_REINCLUDE_PROVIDER-1:
						self.include_provider(excluded_provider)
						self.map_freq_excluded_providers.pop(excluded_provider)
						break
					else:
						self.map_freq_excluded_providers[excluded_provider] += 1
				else:
					self.map_freq_excluded_providers[excluded_provider] = 0

			time.sleep(TIME_CHECK_PROVIDER_ALIVE - ((time.time() - starttime) % TIME_CHECK_PROVIDER_ALIVE))

	def get_registered_providers(self):
		return [self.id_to_provider[provider_id]["provider"] 
					for provider_id in self.list_of_provider_id]

	def get_excluded_providers(self):
		return [excluded_provider for excluded_provider in self.map_freq_excluded_providers.keys()]

	def register_providers(self, providers):
		for provider in providers:
			self.include_provider(provider)

	def include_provider(self,provider):
		# provider is included at the end of the list
		if len(self.list_of_provider_id)>=MAX_NUMBER_REGISTERED_PROVIDERS:
			print(f"maximum capacity reached, cannot inlcude additional provider")
			return

		if not  isinstance(provider, Provider):  
			 print(f"input provider is not a valid instance of Provider")

		provider_id = provider.get_provider_id()
		print(f"include provider, id: {provider_id}")
		self.list_of_provider_id.append(provider_id)
		self.id_to_provider[provider_id]={"provider":provider,"requests":0}

	def exclude_provider(self,provider_id_to_exclude):
		index_provider_to_remove = None
		for index,provider_id in enumerate(self.list_of_provider_id):
			if provider_id == provider_id_to_exclude:
				index_provider_to_remove = index

		if index_provider_to_remove is None:
			print(f"not a valid id {provider_id_to_exclude}")
			return 

		self.list_of_provider_id.remove(provider_id_to_exclude)
		self.id_to_provider.pop(provider_id_to_exclude)		
		print(f"excluded provider, id: {provider_id_to_exclude}")

		# index for round-robin may need to be updated
		if self.round_robin_index>=index_provider_to_remove:
			self.round_robin_index -= (self.round_robin_index-1)
			if self.round_robin_index<0:
				self.round_robin_index = len(self.list_of_provider_id)-1

	def get(self):
		if not len(self.list_of_provider_id):
			raise IndexError("No provider available")
		if self.load_balancer_type == LoadBalancerType.ROUND_ROBIN:
			return self.get_round_robin()
		else:
			return self.get_random_provider()

	def set_load_balancer_type(self,load_balancer_type):
		self.load_balancer_type = load_balancer_type

	def set_load_balancer_type(self):
		return self.load_balancer_type

	def get_random_provider(self):
		random_index = random.randrange(len(self.list_of_provider_id))
		return random_index

	def get_round_robin(self):
		self.round_robin_index += 1
		if self.round_robin_index > (len(self.list_of_provider_id)-1):
			self.round_robin_index = 0
		return self.round_robin_index

	def handle(self,client,request):	
		'''
		The scope of this function is to mock a client-server request response
		scenario. A sleep time has been included before coming back with the reply in 
		order to test the maximum requests limit required in the excercise.
		'''
		with self.lock:
			try:
				provider_index = provider_index_initial = self.get()
			except Exception as e:
				print(f"{e}")
				return ""
			# if provider_index is None:
			# 	raise Exception 
			provider_id = self.list_of_provider_id[provider_index]
			while (self.id_to_provider[provider_id]["requests"] >= 
				self.id_to_provider[provider_id]["provider"].get_max_request_capacity()):
				provider_index = self.get()
				provider_id = self.list_of_provider_id[provider_index]
				if provider_index == provider_index_initial:
					print("Maximum capacity reached for all providers, retry later.")
					return ""

			# increase counter requests and send request 
			self.id_to_provider[provider_id]["requests"]+=1
		
		time.sleep(2)
		response = self.id_to_provider[provider_id]["provider"].handle(client,request,self)

		# decrease counter request once received the response from provider
		with self.lock:
			self.id_to_provider[provider_id]["requests"]-=1
		# send response back to user
		return response


if __name__ == '__main__':
	LoadBalancer()
