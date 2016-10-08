from datetime import timedelta
from unittest import TestCase

from stl.utils import get_natural_str



class UtilsTestCase(TestCase):
	
	def test_get_natural_str(self):
		self.assertEqual(get_natural_str(timedelta(hours=1)), '1 hour')
		self.assertEqual(get_natural_str(timedelta(hours=2)), '2 hours')
		
		self.assertEqual(get_natural_str(timedelta(minutes=1)), '1 minute')
		self.assertEqual(get_natural_str(timedelta(minutes=2)), '2 minutes')
		
		self.assertEqual(get_natural_str(timedelta(seconds=1)), '1 second')
		self.assertEqual(get_natural_str(timedelta(seconds=2)), '2 seconds')
		
		self.assertEqual(get_natural_str(timedelta(seconds=3600+60+1)),
				'1 hour, 1 minute, 1 second')



