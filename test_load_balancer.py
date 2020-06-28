import unittest
import random
import time
import concurrent.futures

from load_balancer import LoadBalancer,MAX_NUMBER_REGISTERED_PROVIDERS
from provider import Provider


class TestLoadBalancer(unittest.TestCase):

	def setUp(self):
		self.load_balancer = LoadBalancer()
		numb_provider = 1
		self.providers = [Provider() for _ in range(numb_provider)]
		self.load_balancer.register_providers(self.providers)

	def test_register_providers(self):
		self.assertEqual(len(self.providers),len(self.load_balancer.get_registered_providers()))
		
	def test_switch_off_one_provider(self):
		index = random.randrange(len(self.providers))
		self.providers[index].turn_off()
		time.sleep(3)# wait before checking
		self.assertEqual(1,len(self.load_balancer.get_excluded_providers()))
		self.assertEqual(len(self.providers)-1,len(self.load_balancer.get_registered_providers()))
		
	def test_switch_off_then_on_provider(self):
		index = random.randrange(len(self.providers))
		self.providers[index].turn_off()
		time.sleep(3)# wait before checking
		self.providers[index].turn_on()
		# checking without waiting
		self.assertEqual(len(self.providers)-1,len(self.load_balancer.get_registered_providers()))
		time.sleep(3)# wait before checking
		self.assertEqual(len(self.providers),len(self.load_balancer.get_registered_providers()))

	def test_too_many_providers(self):
		numb_prov = MAX_NUMBER_REGISTERED_PROVIDERS
		self.providers = [Provider() for _ in range(numb_prov)]
		self.load_balancer.register_providers(self.providers)

	def test_request(self):
		response = self.load_balancer.handle("Client1","Request1")
		self.assertTrue(response)

	def test_exceed_limit_request(self):
		with concurrent.futures.ThreadPoolExecutor() as executor:
			clients = [f"client number {i}" for i in range(20)]
			requests = [f"request number {i}" for i in range(20)]
			results = executor.map(self.load_balancer.handle, clients,requests)
			self.assertTrue(any(not result for result in results))
	
	def test_request_but_no_provider(self):
		for idx in range(len(self.providers)):
			self.providers[idx].turn_off()
		time.sleep(2)
		self.assertRaises(Exception,
			self.load_balancer.handle("Client1","Request1"))


if __name__ == '__main__':
	# Run all tests
	unittest.main()

	# Run single tests
	# suite = unittest.TestSuite()
	# suite.addTest(TestLoadBalancer("test_request_but_no_provider"))
	# runner = unittest.TextTestRunner()
	# runner.run(suite)
	