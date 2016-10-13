from datetime import datetime, timedelta
from itertools import permutations

import logging



class Parser:
	"""
	Provides methods for converting user input into time units.
	"""
	
	def __init__(self, now):
		"""
		Constructor. Expects a datetime instance as argument; the Parser does
		not check time itself.
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
	
	
	def extract_month(self, s):
		"""
		Returns a (year, month) tuple extracted form the given string. Raises
		ValueError if unsuccessful.
		"""
		li = s.split()
		
		if len(li) == 0:
			return self.now.year, self.now.month
		elif len(li) == 1:
			return self.now.year, self._get_month(s)
		elif len(li) == 2:
			combos = self._try([self._get_year, self._get_month], li)
			if len(combos) != 1:
				raise ValueError('Could not infer month: {}'.format(s))
			
			return combos[0][0], combos[0][1]
		
		else:
			raise ValueError('Could not infer month: {}'.format(s))
	
	
	def extract_date(self, s):
		"""
		Returns a (year, month, day) tuple extracted from the given string.
		Raises ValueError if unsuccessful.
		"""
		li = s.split()
		
		if len(li) == 0:
			return self.now.year, self.now.month, self.now.day
		elif len(li) == 1:
			return self.now.year, self.now.month, self._get_day(li[0])
		
		elif len(li) == 2:
			combos = self._try([self._get_month, self._get_day], li)
			if len(combos) != 1:
				raise ValueError('Could not infer date: {}'.format(s))
			
			return self.now.year, combos[0][0], combos[0][1]
		
		elif len(li) == 3:
			combos = self._try([self._get_year, self._get_month, self._get_day], li)
			if len(combos) != 1:
				raise ValueError('Could not infer date: {}'.format(s))
			
			return combos[0][0], combos[0][1], combos[0][2]
		
		else:
			raise ValueError('Could not infer date: {}'.format(s))



def prettify_delta(delta):
	"""
	Returns a natural string representing the given timedelta. The biggest unit
	is the hour, because a working day is too ambiguous.
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
	
	return ', '.join(li)



