from datetime import date, datetime, timedelta
from itertools import permutations

import logging



"""
The str(f|p)time format for ISO datetime strings with minute-precision and the
expected length for such strings.
"""
ISO_FORMAT = '%Y-%m-%dT%H:%M'
ISO_FORMAT_LEN = 16



class Parser:
	"""
	Provides methods for converting user input into time units.
	"""
	
	def __init__(self, now=None):
		"""
		Constructor. Expects a datetime instance as argument; the Parser does
		not check the time itself.
		"""
		self.now = now
		self.log = logging.getLogger(__name__)
	
	
	def _try(self, funcs, args):
		"""
		Expects a [] of one-argument functions and a [] of arguments. Keeping
		the order of the funcs, tries all permutations of the args and returns
		[(func_result,),] of the combinations that did not raise ValueError.
		
		Of course, the number of funcs and args must be equal.
		"""
		combos = []
		
		for args_li in permutations(args):
			res_li = []
			try:
				for index, arg in enumerate(args_li):
					res_li.append(funcs[index](arg))
			except ValueError:
				pass
			else:
				combos.append(tuple(res_li))
		
		return combos
	
	
	def _get_year(self, s):
		"""
		Returns the year represented by the given string by trying the year
		strptime directives. Raises ValueError if unsuccessful.
		"""
		for code in ['%Y', '%y']:
			try:
				dt = datetime.strptime(s, code)
			except ValueError:
				continue
			else:
				return dt.year
		else:
			raise ValueError('Could not extract year: {}'.format(s))
	
	
	def _get_month(self, s):
		"""
		Returns the month represented by the given string by trying the month
		strptime directives. Raises ValueError if unsuccessful.
		"""
		s = s.lower()
		
		for code in ['%m', '%b', '%B']:
			try:
				dt = datetime.strptime(s, code)
			except ValueError:
				continue
			else:
				return dt.month
		else:
			raise ValueError('Could not extract month: {}'.format(s))
	
	
	def _get_day(self, s):
		"""
		Returns the day represented by the given string by trying the day
		strptime directive. Raises ValueError if unsuccessful.
		"""
		try:
			dt = datetime.strptime(s, '%d')
		except ValueError:
			raise ValueError('Could not extract day: {}'.format(s))
		else:
			return dt.day
	
	
	def extract_year(self, s):
		"""
		Returns the year extracted from the given string. Raises ValueError if
		unsuccessful.
		"""
		if not len(s) or s.lower() == 'this':
			return self.now.year
		
		if s.lower() == 'last':
			return self.now.year - 1
		
		return self._get_year(s)
	
	
	def extract_month(self, s):
		"""
		Returns a (year, month) tuple extracted form the given string. Raises
		ValueError if unsuccessful.
		"""
		li = s.split()
		
		if len(li) == 0:
			return self.now.year, self.now.month
		
		elif len(li) == 1:
			if s.lower() == 'last':
				month = self.now.month - 1 or 12
				year = self.now.year - 1 if month == 12 else self.now.year
			elif s.lower() == 'this':
				month = self.now.month
				year = self.now.year
			else:
				month = self._get_month(s)
				year = self.now.year
			
			return year, month
		
		elif len(li) == 2:
			combos = self._try([self._get_year, self._get_month], li)
			if len(combos) != 1:
				raise ValueError('Could not infer month: {}'.format(s))
			
			return combos[0][0], combos[0][1]
		
		else:
			raise ValueError('Could not infer month: {}'.format(s))
	
	
	def extract_week(self, s):
		"""
		Returns a (date1, date2) tuple with date1 being a Monday and date2
		being a Sunday defining the week extracted from the given string.
		Raises ValueError if unsuccessful.
		"""
		monday = self.now.date() - timedelta(days=self.now.weekday())
		sunday = monday + timedelta(days=6)
		
		li = s.split()
		
		if len(li) == 0:
			return monday, sunday
		
		elif len(li) == 1:
			if s.lower() == 'last':
				monday = monday - timedelta(days=7)
				sunday = sunday - timedelta(days=7)
			elif s.lower() == 'this':
				pass
			else:
				raise ValueError('Could not infer week: {}'.format(s))
			
			return monday, sunday
		
		else:
			raise ValueError('Could not infer week: {}'.format(s))
	
	
	def extract_date(self, s):
		"""
		Returns a date instance extracted from the given string. Raises
		ValueError if unsuccessful.
		
		Apart from the _get_(year|month|day) permutations, this method also
		recognises the ISO date format and words like today and yesterday.
		"""
		li = s.split()
		
		if len(li) == 0:
			return self.now.date()
		
		elif len(li) == 1:
			try:
				dt = datetime.strptime(s, '%Y-%m-%d')
			except ValueError:
				pass
			else:
				return dt.date()
			
			if s.lower() in ['last', 'yesterday']:
				return self.now.date() - timedelta(days=1)
			elif s.lower() in ['this', 'today']:
				return self.now.date()
			else:
				day = self._get_day(li[0])
				return date(self.now.year, self.now.month, day)
		
		elif len(li) == 2:
			combos = self._try([self._get_month, self._get_day], li)
			if len(combos) != 1:
				raise ValueError('Could not infer date: {}'.format(s))
			
			return date(self.now.year, combos[0][0], combos[0][1])
		
		elif len(li) == 3:
			combos = self._try([self._get_year, self._get_month, self._get_day], li)
			if len(combos) != 1:
				raise ValueError('Could not infer date: {}'.format(s))
			
			return date(combos[0][0], combos[0][1], combos[0][2])
		
		else:
			raise ValueError('Could not infer date: {}'.format(s))
	
	
	def extract_datetime(self, s):
		"""
		Returns a datetime instance extracted from the given string. Unlike the
		previous few methods, this one only accepts ISO format strings (the
		seconds being optional).
		"""
		try:
			dt = datetime.strptime(s[:ISO_FORMAT_LEN], ISO_FORMAT)
		except ValueError:
			raise ValueError('Could not infer datetime: {}'.format(s))
		
		return dt
	
	
	def _extract_span(self, tokens):
		"""
		Helper for the extract_span method. Parses the already tokenised input
		string and returns two date instances. This method does not try to
		catch any exceptions: this is done by extract_span.
		"""
		tags = []
		for token in tokens:
			if token.isdigit():
				if len(token) == 4: tags.append('y')
				else: tags.append('d')
			else: tags.append('m')
		
		if set(tags[-3:]) == set(['d', 'm', 'y']):
			assert len(tokens) in [3, 4, 5, 6]
			
			d2 = date(self._get_year(tokens[-3:][tags[-3:].index('y')]),
					self._get_month(tokens[-3:][tags[-3:].index('m')]),
					self._get_day(tokens[-3:][tags[-3:].index('d')]))
			
			if len(tokens) == 6:
				assert set(tags[:3]) == set(['d', 'm', 'y'])
				d1 = date(self._get_year(tokens[tags[:3].index('y')]),
						self._get_month(tokens[tags[:3].index('m')]),
						self._get_day(tokens[tags[:3].index('d')]))
			elif len(tokens) == 5:
				assert set(tags[:2]) == set(['d', 'm'])
				d1 = date(d2.year,
						self._get_month(tokens[tags[:2].index('m')]),
						self._get_day(tokens[tags[:2].index('d')]))
			elif len(tokens) == 4:
				assert tags[0] == 'd'
				d1 = date(d2.year, d2.month)
			elif len(tokens) == 3:
				d1 = self.now.date()
		
		elif set(tags[-2:]) == set(['d', 'm']):
			assert len(tokens) in [2, 3, 4]
			
			d2 = date(self.now.year,
					self._get_month(tokens[-2:][tags[-2:].index('m')]),
					self._get_day(tokens[-2:][tags[-2:].index('d')]))
			
			if len(tokens) == 4:
				assert set(tags[:2]) == set(['d', 'm'])
				d1 = date(d2.year,
						self._get_month(tokens[tags[:2].index('m')]),
						self._get_day(tokens[tags[:2].index('d')]))
			elif len(tokens) == 3:
				assert tags[0] == 'd'
				d1 = date(d2.year, d2.month, self._get_day(tokens[0]))
			elif len(tokens) == 2:
				d1 = self.now.date()
		
		elif tags[-1] == 'd':
			assert len(tokens) in [1, 2]
			
			d2 = date(self.now.year, self.now.month, self._get_day(tokens[-1]))
			
			if len(tokens) == 2:
				assert tags[0] == 'd'
				d1 = date(d2.year, d2.month, self._get_day(tokens[0]))
			elif len(tokens) == 1:
				d1 = self.now.date()
		
		else:
			raise ValueError
		
		return d1, d2
	
	
	def extract_span(self, s):
		"""
		Returns a (d1, d2) tuple of date instances extracted from the given
		string. The earlier date will be first even if it was not first in the
		string.
		"""
		tokens = s.split()
		
		if len(tokens) < 1 or len(tokens) > 6:
			raise ValueError('Could not infer dates: {}'.format(s))
		
		try:
			d1, d2 = self._extract_span(tokens)
		except (AssertionError, ValueError) as err:
			self.log.debug(str(err))
			raise ValueError('Could not infer dates: {}'.format(s))
		
		if d2 < d1:
			d1, d2 = d2, d1
		
		return d1, d2



"""
Functions that convert time units into pretty strings for human consumption
"""

def prettify_date(year, month, day=None):
	"""
	Returns a human-readable string representing the date defined by the given
	parameters.
	"""
	if day:
		d = date(year, month, day)
		s = d.strftime('%d %b %Y')
	else:
		d = date(year, month, 1)
		s = d.strftime('%b %Y')
	
	return s.lower()



def prettify_datetime(dt):
	"""
	Returns a pretty string representing the given datetime instance. Units
	smaller than minutes are not included.
	"""
	return ' '.join([
		prettify_date(dt.year, dt.month, dt.day),
		dt.strftime('%H:%M')
	])



def prettify_delta(delta):
	"""
	Returns a human-readable string representing the given timedelta. The
	biggest unit is the hour, because a working day is too ambiguous.
	"""
	d = {}
	
	d['minutes'], d['seconds'] = divmod(int(delta.total_seconds()), 60)
	d['hours'], d['minutes'] = divmod(d['minutes'], 60)
	
	li = []
	
	for unit in ('hours', 'minutes', 'seconds'):
		if d[unit]:
			s = str(d[unit])+' '+unit
			if d[unit] == 1:
				s = s[:-1]
			li.append(s)
	
	s = ', '.join(li)
	if not s: s = '-'
	
	return s
