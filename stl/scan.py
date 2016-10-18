from datetime import datetime

import logging
import re



"""
List of datetime directives that are understood by the Scanner
"""
DIRECTIVES = ['%Y', '%y', '%m', '%b', '%B', '%d', '%H', '%M', '%S']



class Scanner:
	"""
	Inited with a regex pattern, an instance can go over input files and use
	the pattern to extract log entries from the matching lines.
	"""
	
	def __init__(self, line_pattern, year=None, month=None, day=None):
		"""
		Constructor. Expects a regex pattern that contains at least two named
		groups: start, stop, and, optionally, task. The pattern will be matched
		against every input line in order to harvest log entries.
		"""
		self.log = logging.getLogger(__name__)
		
		try:
			self.regex = re.compile(self._normalise_pattern(line_pattern))
		except re.error as err:
			self.log.error(str(err))
			raise ValueError('Could not compile regex pattern')
		
		self.year = year
		self.month = month
		self.day = day
	
	
	def _normalise_pattern(self, pattern):
		"""
		Regex patterns accepted by the Scanner are the normal regexes but also
		include the datetime directives. The latter are here replaced by regex
		named groups.
		"""
		for directive in DIRECTIVES:
			count = 0
			
			while True:
				pos = pattern.find(directive)
				if pos == -1:
					break
				
				named_group = '(?P<{}{}>)'.format(directive[1], count)
				pattern = pattern[:pos] + named_group + pattern[pos+2:]
				
				count += 1
				if count > 2:
					err = 'Could not understand pattern: found {} twice'
					raise ValueError(err.format(directive))
		
		return pattern
	
	
	def scan_line(self, line):
		"""
		Returns the {start, stop, task} log entry found in the given string or
		None if there is no match. Raises ValueError if there is a problem.
		"""
		match = self.regex.match(line)
		if match is None:
			return None
		
		
		
		if start > stop:
			raise ValueError('Negative time interval: from {} to {}'.format(start, stop))
		
		return {'start': start, 'stop': stop, 'task': task}
	
	
	def scan_file(self, file_path):
		"""
		Returns [] of the {start, stop, task} log entries found in the given
		file. Raises ValueError upon encountering a problem.
		"""
		entries = []
		
		try:
			with open(file_path) as f:
				for line in f:
					entry = self.scan_line(line)
					if entry:
						entries.append(entry)
		except IOError as err:
			self.log.error(str(err))
			raise ValueError('Could not open file: {}'.format(file_path))
		
		return entries



