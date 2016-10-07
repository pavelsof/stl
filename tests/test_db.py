from datetime import datetime

import os.path

from tempfile import TemporaryDirectory
from unittest import TestCase

from stl.db import DatabaseError, Database



class DatabaseTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
		self.db = Database(self.temp_dir.name)
	
	def tearDown(self):
		self.temp_dir.cleanup()
	
	def test_current(self):
		self.assertIsNone(self.db.get_current())
		
		now = datetime.now()
		self.db.add_current(now, 'testing')
		
		entry = self.db.get_current()
		self.assertEqual(entry['stamp'].year, now.year)
		self.assertEqual(entry['stamp'].month, now.month)
		self.assertEqual(entry['stamp'].day, now.day)
		self.assertEqual(entry['stamp'].hour, now.hour)
		self.assertEqual(entry['stamp'].minute, now.minute)
		self.assertEqual(entry['text'], 'testing')
		
		entry = self.db.get_current(delete=True)
		self.assertEqual(entry['stamp'].year, now.year)
		self.assertEqual(entry['stamp'].month, now.month)
		self.assertEqual(entry['stamp'].day, now.day)
		self.assertEqual(entry['stamp'].hour, now.hour)
		self.assertEqual(entry['stamp'].minute, now.minute)
		self.assertEqual(entry['text'], 'testing')
		
		self.assertIsNone(self.db.get_current())



