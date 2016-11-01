import os
import shutil

from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis.extra.datetime import dates, datetimes
from hypothesis.strategies import dictionaries, fixed_dictionaries
from hypothesis.strategies import lists, text
from hypothesis import assume, given

from stl.db import ARCHIVE_DT_FORMAT
from stl.db import Database



class DatabaseTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
		self.db = Database(self.temp_dir.name)
	
	
	def tearDown(self):
		self.temp_dir.cleanup()
	
	
	def _check_dt_equal(self, dt1, dt2, seconds=False):
		self.assertEqual(dt1.year, dt2.year)
		self.assertEqual(dt1.month, dt2.month)
		self.assertEqual(dt1.day, dt2.day)
		self.assertEqual(dt1.hour, dt2.hour)
		self.assertEqual(dt1.minute, dt2.minute)
		if seconds:
			self.assertEqual(dt1.second, dt2.second)
	
	
	@given(datetimes(allow_naive=True, timezones=[]))
	def test_get_path_with_create(self, dt):
		file_path = self.db.get_path(dt.year, dt.month, create=True)
		dir_path = os.path.dirname(file_path)
		self.assertTrue(os.path.exists(dir_path))
	
	
	@given(datetimes(allow_naive=True, timezones=[]), text())
	def test_add_and_get_current(self, dt, t):
		self.db.add_current(dt, t)
		
		entry = self.db.get_current()
		self._check_dt_equal(entry['stamp'], dt, seconds=True)
		self.assertEqual(entry['task'], self.db._sanitise_text(t))
		
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
		
		logs = self.db.get_month(dt1.year, dt1.month)
		self.assertEqual(len(logs), 1)
		self._check_dt_equal(logs[0]['start'], dt1)
		self._check_dt_equal(logs[0]['stop'], dt2)
		self.assertEqual(logs[0]['task'], self.db._sanitise_text(t))
		
		path = os.path.join(self.temp_dir.name,
			str(dt1.year).zfill(4), str(dt1.month).zfill(2))
		self.assertTrue(os.path.exists(path))
		os.remove(path)
	
	
	@given(lists(fixed_dictionaries({
			'start': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'task': text()})))
	def test_add_complete_with_sort(self, li):
		assume(len(li) == len(set([  # avoid dts that can be sorted either way
			d['start'].strftime(ARCHIVE_DT_FORMAT) for d in li])))
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['task'], append=False)
		
		for month in range(1, 13):
			month_li = list(filter(lambda d: d['start'].month == month, li))
			month_li = list(sorted(month_li, key=lambda d: d['start']))
			
			logs = self.db.get_month(2000, month)
			self.assertEqual(len(logs), len(month_li))
			
			for i in range(0, len(logs)):
				self._check_dt_equal(logs[i]['start'], month_li[i]['start'])
				self._check_dt_equal(logs[i]['stop'], month_li[i]['stop'])
				self.assertEqual(logs[i]['task'], self.db._sanitise_text(month_li[i]['task']))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)
	
	
	@given(lists(fixed_dictionaries({
			'start': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'task': text()})))
	def test_get_month(self, li):
		li = list(sorted(li, key=lambda d: d['start']))
		
		for month in range(1, 13):
			self.assertEqual(self.db.get_month(2000, month), [])
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['task'])
		
		for month in range(1, 13):
			li_ = list(filter(lambda d: d['start'].month == month, li))
			entries = self.db.get_month(2000, month)
			self.assertEqual(len(entries), len(li_))
			for i, entry in enumerate(entries):
				self._check_dt_equal(entry['start'], li_[i]['start'])
				self._check_dt_equal(entry['stop'], li_[i]['stop'])
				self.assertEqual(entry['task'], self.db._sanitise_text(li_[i]['task']))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)
	
	
	@given(lists(fixed_dictionaries({
			'start': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2000, timezones=[]),
			'task': text()})))
	def test_get_year(self, li):
		li = list(sorted(li, key=lambda d: d['start']))
		
		self.assertEqual(self.db.get_year(2000), [])
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['task'])
		
		entries = self.db.get_year(2000)
		self.assertEqual(len(entries), len(li))
		for i, entry in enumerate(entries):
			self._check_dt_equal(entry['start'], li[i]['start'])
			self._check_dt_equal(entry['stop'], li[i]['stop'])
			self.assertEqual(entry['task'], self.db._sanitise_text(li[i]['task']))
		
		year_dir = os.path.join(self.temp_dir.name, '2000')
		if os.path.exists(year_dir):
			shutil.rmtree(year_dir)
	
	
	@given(lists(fixed_dictionaries({  # min and max year set for gen speed
			'start': datetimes(min_year=2000, max_year=2100, timezones=[]),
			'stop': datetimes(min_year=2000, max_year=2100, timezones=[]),
			'task': text()}), min_size=1))
	def test_get_span(self, li):
		li = list(sorted(li, key=lambda d: d['start']))
		first = li[0]['start'].date()
		last = li[-1]['start'].date()
		
		for d in li:
			self.db.add_complete(d['start'], d['stop'], d['task'])
		
		span = self.db.get_span(first, last)
		self.assertEqual(len(span), len(li))
		
		for subdir in os.listdir(self.temp_dir.name):
			shutil.rmtree(os.path.join(self.temp_dir.name, subdir))
	
	
	@given(dictionaries(
			keys = text(),
			values = lists(dates(), min_size=1)))
	def test_add_and_get_task(self, d):
		d = {task: dts for task, dts in d.items()
				if self.db._sanitise_text(task)}
		
		for task, dts in d.items():
			for dt in dts:
				self.db.add_task(task, dt.year, dt.month)
		
		for task, dts in d.items():
			li = list(set([(dt.year, dt.month) for dt in dts]))
			res = self.db.get_task(task)
			self.assertEqual(list(sorted(li)), list(sorted(res)))
		
		path = os.path.join(self.temp_dir.name, 'tasks')
		if os.path.exists(path):
			os.remove(path)



