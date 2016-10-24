from datetime import timedelta

import os.path
import shutil

from tempfile import TemporaryDirectory
from unittest.mock import patch
from unittest import TestCase

from hypothesis.extra.datetime import datetimes
from hypothesis.strategies import text
from hypothesis import assume, given

from stl.core import Core



class CoreTestCase(TestCase):
	
	def setUp(self):
		self.temp_dir = TemporaryDirectory()
		
		with patch.object(Core, '_get_dir_path',
				return_value=self.temp_dir.name) as mock_method:
			self.core = Core()
			mock_method.assert_called_once_with()
			self.assertEqual(self.core.dir_path, self.temp_dir.name)
	
	
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
	
	
	def test_init_with_bad_dir(self):
		keine_dir = os.path.join(self.temp_dir.name, 'keine')
		with self.assertRaises(ValueError):
			Core(dir_path=keine_dir)
	
	
	@given(datetimes(timezones=[]), text())
	def test_start(self, dt, t):
		res = self.core.start(t, now=dt)
		self.assertTrue(res.startswith('started'))
		
		with self.assertRaises(ValueError):
			self.core.start(t, now=dt)
		
		entry = self.core.db.get_current(delete=True)
		self._check_dt_equal(entry['stamp'], dt, seconds=True)
		self.assertEqual(entry['task'], self.core.db._sanitise_text(t))
	
	
	@given(datetimes(min_year=1000, timezones=[]),
			datetimes(min_year=1000, timezones=[]))
	def test_stop(self, dt1, dt2):
		assume(dt1 < dt2)
		self.core.start('lumberjacking', now=dt1)
		
		res = self.core.stop(now=dt2)
		self.assertTrue(res.startswith('stopped'))
		
		res = self.core.db.get_day(dt1.year, dt1.month, dt1.day)[0]
		self._check_dt_equal(res['start'], dt1)
		self._check_dt_equal(res['stop'], dt2)
		self.assertEqual(res['task'], 'lumberjacking')
		
		self.assertIsNone(self.core.db.get_current())
		
		with self.assertRaises(ValueError):
			self.core.stop(now=dt2)
		
		year_dir = os.path.join(self.temp_dir.name, str(dt1.year))
		shutil.rmtree(year_dir)
	
	
	@given(datetimes(min_year=1000, timezones=[]),
			datetimes(min_year=1000, timezones=[]),
			text())
	def test_add(self, dt1, dt2, t):
		assume(dt1 < dt2 and dt2 - dt1 > timedelta(minutes=1))
		self.core.add(dt1.isoformat(), dt2.isoformat(), t)
		
		res = self.core.db.get_day(dt1.year, dt1.month, dt1.day)[0]
		self._check_dt_equal(res['start'], dt1)
		self._check_dt_equal(res['stop'], dt2)
		self.assertEqual(res['task'], self.core.db._sanitise_text(t))
		
		with self.assertRaises(ValueError):
			self.core.add(dt2.isoformat(), dt1.isoformat(), t)
		
		year_dir = os.path.join(self.temp_dir.name, str(dt1.year))
		shutil.rmtree(year_dir)



