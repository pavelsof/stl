from unittest import TestCase

from stl.scan import DIRECTIVES, Scanner



class ScannerTestCase(TestCase):
	
	def setUp(self):
		self.scanner = Scanner('')
	
	def test_normalise_pattern(self):
		li = [
			('%Y-%m-%d', '(?P<Y0>)-(?P<m0>)-(?P<d0>)'),
			('%H:%M', '(?P<H0>):(?P<M0>)'),
			('%H:%M-%H:%M', '(?P<H0>):(?P<M0>)-(?P<H1>):(?P<M1>)')]
		
		for a, b in li:
			self.assertEqual(self.scanner._normalise_pattern(a), b)
		
		with self.assertRaises(ValueError):
			self.scanner._normalise_pattern('%H:%M-%H:%M-%H:%M')



