import unittest
import test_load_balancer

if __name__ == '__main__':
	print("Running test scripts")

	suite = unittest.TestLoader().loadTestsFromModule(test_load_balancer)
	unittest.TextTestRunner(verbosity=2).run(suite)