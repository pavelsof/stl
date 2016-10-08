from datetime import datetime

import os.path
import shutil

from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis.extra.datetime import datetimes
from hypothesis.strategies import fixed_dictionaries, lists, text
from hypothesis import given

from stl.db import DatabaseError, Database



class DatabaseTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
		self.db = Database(self.temp_dir.name)
	
	def tearDown(self):
		self.temp_dir.cleanup()
	
	
	@given(datetimes(allow_naive=True, timezones=[]))
	def test_get_path_with_create(self, dt):
		file_path = self.db._get_path(dt.year, dt.month, create=True)
		dir_path = os.path.dirname(file_path)
		self.assertTrue(os.path.exists(dir_path))
	
	
	@given(datetimes(allow_naive=True, timezones=[]), text())
	def test_add_and_get_current(self, dt, t):
		self.db.add_current(dt, t)
		
		entry = self.db.get_current()
		self.assertEqual(entry['stamp'].year, dt.year)
		self.assertEqual(entry['stamp'].month, dt.month)
		self.assertEqual(entry['stamp'].day, dt.day)
		self.assertEqual(entry['stamp'].hour, dt.hour)
		self.assertEqual(entry['stamp'].minute, dt.minute)
		self.assertEqual(entry['text'], self.db._sanitise_text(t))
		
		path = os.path.join(self.temp_dir.name, 'current')
		self.assertTrue(os.path.exists(path))
	
	
	@given(datetimes(allow_naive=True, timezones=[]), text())
	def test_get_current_when_none(self, dt, t):
		self.assertIsNone(self.db.get_current())
		
		self.db.add_current(dt, t)
		res1 = self.db.get_current()
		res2 = self.db.get_current(delete=True)
		
		self.assertEqual(res1, res2)
		self.assertIsNone(self.db.get_current())
	
	
	@given(datetimes(timezones=[]), datetimes(timezones=[]), text())
	def test_add_complete(self, dt1, dt2, t):
		self.db.add_complete(dt1, dt2, t)
		
		path = os.path.join(self.temp_dir.name,
			str(dt1.year).zfill(4), str(dt1.month).zfill(2))
		self.assertTrue(os.path.exists(path))
	
	
	@given(lists(fixed_dictionaries({
			'start': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'text': text()})))
	def test_get_month(self, li):
		for month in range(1, 13):
			self.assertEqual(self.db.get_month(2000, month), [])
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['text'])
		
		for month in range(1, 13):
			li_ = list(filter(lambda d: d['start'].month == month, li))
			entries = self.db.get_month(2000, month)
			self.assertEqual(len(entries), len(li_))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)



