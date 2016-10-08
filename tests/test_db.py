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
	
	def _check_dt_equal(self, dt1, dt2):
		self.assertEqual(dt1.year, dt2.year)
		self.assertEqual(dt1.month, dt2.month)
		self.assertEqual(dt1.day, dt2.day)
		self.assertEqual(dt1.hour, dt2.hour)
		self.assertEqual(dt1.minute, dt2.minute)
	
	
	@given(datetimes(allow_naive=True, timezones=[]))
	def test_get_path_with_create(self, dt):
		file_path = self.db._get_path(dt.year, dt.month, create=True)
		dir_path = os.path.dirname(file_path)
		self.assertTrue(os.path.exists(dir_path))
	
	
	@given(datetimes(allow_naive=True, timezones=[]), text())
	def test_add_and_get_current(self, dt, t):
		self.db.add_current(dt, t)
		
		entry = self.db.get_current()
		self._check_dt_equal(entry['stamp'], dt)
		self.assertEqual(entry['tag'], self.db._sanitise_text(t))
		
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
			'tag': text()})))
	def test_get_month(self, li):
		li = list(sorted(li, key=lambda d: d['start']))
		
		for month in range(1, 13):
			self.assertEqual(self.db.get_month(2000, month), [])
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['tag'])
		
		for month in range(1, 13):
			li_ = list(filter(lambda d: d['start'].month == month, li))
			entries = self.db.get_month(2000, month)
			self.assertEqual(len(entries), len(li_))
			for i, entry in enumerate(entries):
				self._check_dt_equal(entry['start'], li_[i]['start'])
				self._check_dt_equal(entry['stop'], li_[i]['stop'])
				self.assertEqual(entry['tag'], self.db._sanitise_text(li_[i]['tag']))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)
	
	
	@given(lists(fixed_dictionaries({
			'start': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'tag': text()})))
	def test_get_year(self, li):
		li = list(sorted(li, key=lambda d: d['start']))
		
		self.assertEqual(self.db.get_year(2000), [])
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['tag'])
		
		entries = self.db.get_year(2000)
		self.assertEqual(len(entries), len(li))
		for i, entry in enumerate(entries):
			self._check_dt_equal(entry['start'], li[i]['start'])
			self._check_dt_equal(entry['stop'], li[i]['stop'])
			self.assertEqual(entry['tag'], self.db._sanitise_text(li[i]['tag']))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)



