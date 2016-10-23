from datetime import date, datetime, timedelta
from itertools import permutations
from unittest import TestCase

from hypothesis.extra.datetime import dates, datetimes
from hypothesis.strategies import just, sampled_from
from hypothesis import given

from stl.time import Parser
from stl.time import prettify_date, prettify_datetime, prettify_delta



class ParserTestCase(TestCase):
	
	def setUp(self):
		self.now = datetime(2016, 10, 15)
		self.parser = Parser(self.now)
	
	
	@given(dates(min_year=1000))
	def test_extract_year(self, d):
		s = d.strftime('%Y')
		year = self.parser.extract_year(s)
		self.assertEqual(year, d.year)
	
	
	@given(dates(min_year=1000),
			just('%Y'),
			sampled_from(['%m', '%b', '%B']))
	def test_extract_month(self, d, y_code, m_code):
		for perm in permutations([y_code, m_code]):
			s = d.strftime(' '.join(perm))
			year, month = self.parser.extract_month(s)
			self.assertEqual(year, d.year)
			self.assertEqual(month, d.month)
		
		s = d.strftime(m_code)
		year, month = self.parser.extract_month(s)
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, d.month)
	
	
	def test_extract_week(self):
		monday, sunday = self.parser.extract_week('')
		self.assertEqual(monday, date(2016, 10, 10))
		self.assertEqual(sunday, date(2016, 10, 16))
		
		monday, sunday = self.parser.extract_week('this')
		self.assertEqual(monday, date(2016, 10, 10))
		self.assertEqual(sunday, date(2016, 10, 16))
		
		monday, sunday = self.parser.extract_week('last')
		self.assertEqual(monday, date(2016, 10, 3))
		self.assertEqual(sunday, date(2016, 10, 9))
	
	
	@given(dates(min_year=1000),
			just('%Y'),
			sampled_from(['%b', '%B']),
			sampled_from(['%d']))
	def test_extract_date(self, d, y_code, m_code, d_code):
		for perm in permutations([y_code, m_code, d_code]):
			s = d.strftime(' '.join(perm))
			year, month, day = self.parser.extract_date(s)
			self.assertEqual(year, d.year)
			self.assertEqual(month, d.month)
			self.assertEqual(day, d.day)
		
		for perm in permutations([m_code, d_code]):
			s = d.strftime(' '.join(perm))
			year, month, day = self.parser.extract_date(s)
			self.assertEqual(year, self.now.year)
			self.assertEqual(month, d.month)
			self.assertEqual(day, d.day)
		
		s = d.strftime(d_code)
		year, month, day = self.parser.extract_date(s)
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		self.assertEqual(day, d.day)
	
	
	@given(dates(min_year=1000))
	def test_extract_date_iso(self, d):
		year, month, day = self.parser.extract_date(d.isoformat())
		self.assertEqual(year, d.year)
		self.assertEqual(month, d.month)
		self.assertEqual(day, d.day)
	
	
	def test_extract_words(self):
		year = self.parser.extract_year('last')
		self.assertEqual(year, self.now.year-1)
		
		year, month = self.parser.extract_month('last')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month-1)
		
		year, month, day = self.parser.extract_date('last')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		self.assertEqual(day, self.now.day-1)
		
		year, month, day = self.parser.extract_date('yesterday')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		self.assertEqual(day, self.now.day-1)
		
		year, month, day = self.parser.extract_date('today')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		self.assertEqual(day, self.now.day)
	
	
	def test_extract_empty_strings(self):
		year = self.parser.extract_year('')
		self.assertEqual(year, self.now.year)
		
		year, month = self.parser.extract_month('')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		
		year, month, day = self.parser.extract_date('')
		self.assertEqual(year, self.now.year)
		self.assertEqual(month, self.now.month)
		self.assertEqual(day, self.now.day)
	
	
	@given(datetimes(timezones=[]))
	def test_extract_datetime(self, dt):
		res = self.parser.extract_datetime(dt.isoformat())
		
		for prop in ['year', 'month', 'day', 'hour', 'minute']:
			self.assertEqual(getattr(res, prop), getattr(dt, prop))



class PrettifyTestCase(TestCase):
	
	def setUp(self):
		self.now = datetime(2016, 10, 15)
		self.parser = Parser(self.now)
	
	
	@given(dates(min_year=1000))
	def test_prettify_date(self, d):
		s = prettify_date(d.year, d.month, d.day)
		year, month, day = self.parser.extract_date(s)
		self.assertEqual(year, d.year)
		self.assertEqual(month, d.month)
		self.assertEqual(day, d.day)
		
		s = prettify_date(d.year, d.month)
		year, month = self.parser.extract_month(s)
		self.assertEqual(year, d.year)
		self.assertEqual(month, d.month)
	
	
	@given(datetimes(min_year=1000, timezones=[]))
	def test_prettify_datetime(self, dt):
		s = prettify_datetime(dt)
		parts = s.rsplit(maxsplit=1)
		
		year, month, day = self.parser.extract_date(parts[0])
		self.assertEqual(year, dt.year)
		self.assertEqual(month, dt.month)
		self.assertEqual(day, dt.day)
		
		hour, minute = map(int, parts[1].split(':'))
		self.assertEqual(hour, dt.hour)
		self.assertEqual(minute, dt.minute)
	
	
	def test_prettify_delta(self):
		self.assertEqual(prettify_delta(timedelta(hours=1)), '1 hour')
		self.assertEqual(prettify_delta(timedelta(hours=2)), '2 hours')
		
		self.assertEqual(prettify_delta(timedelta(minutes=1)), '1 minute')
		self.assertEqual(prettify_delta(timedelta(minutes=2)), '2 minutes')
		
		self.assertEqual(prettify_delta(timedelta(seconds=1)), '1 second')
		self.assertEqual(prettify_delta(timedelta(seconds=2)), '2 seconds')
		
		self.assertEqual(prettify_delta(timedelta(seconds=3600+60+1)),
				'1 hour, 1 minute, 1 second')



