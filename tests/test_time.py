from datetime import datetime, timedelta
from itertools import permutations
from unittest import TestCase

from hypothesis.extra.datetime import dates
from hypothesis.strategies import just, sampled_from
from hypothesis import given

from stl.time import Parser, prettify_delta



class ParserTestCase(TestCase):
	
	def setUp(self):
		self.now = datetime(2016, 10, 15)
		self.parser = Parser(self.now)
	
	
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



class PrettifyTestCase(TestCase):
	
	def test_prettify_delta(self):
		self.assertEqual(prettify_delta(timedelta(hours=1)), '1 hour')
		self.assertEqual(prettify_delta(timedelta(hours=2)), '2 hours')
		
		self.assertEqual(prettify_delta(timedelta(minutes=1)), '1 minute')
		self.assertEqual(prettify_delta(timedelta(minutes=2)), '2 minutes')
		
		self.assertEqual(prettify_delta(timedelta(seconds=1)), '1 second')
		self.assertEqual(prettify_delta(timedelta(seconds=2)), '2 seconds')
		
		self.assertEqual(prettify_delta(timedelta(seconds=3600+60+1)),
				'1 hour, 1 minute, 1 second')


