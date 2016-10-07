import csv

from datetime import datetime

import logging
import os



"""
The str(f|p)time formats used in the database files.
"""
DT_FORMAT_FULL = '%Y-%m-%d %H:%M'
DT_FORMAT_SHORT = '%d %H:%M'



class DatabaseError(ValueError):
	"""
	Raised when writing or retrieving data fails.
	"""
	pass



class Database:
	"""
	Handles adding and retrieving log entries. There are two types of log
	entries depending on whether the task is stopped (closed) or not (open).
	There can be only one open entry at a time and it is kept in a single file
	named `current`. The closed ones are kept separately, one file per month,
	grouped in directories by year.
	"""
	
	def __init__(self, dir_path):
		"""
		Constructor. The path should lead to a directory at stl's disposal for
		creating and editing files in.
		"""
		self.log = logging.getLogger(__name__)
		self.dir_path = dir_path
	
	
	def _get_path(self, year, month, create=False):
		"""
		Returns the absolute path to the file containing the logs for the given
		year and month.
		"""
		year_dir = os.path.join(self.dir_path, str(year))
		
		if create and not os.path.exists(year_dir):
			try:
				os.mkdir(year_dir)
			except:
				raise DatabaseError('Could not create database subdir')
			else:
				self.log.debug('Created dir '+year_dir)
		
		return os.path.join(year_dir, str(month).zfill(2))
	
	
	def add_current(self, stamp, text=''):
		"""
		Creates a new open log entry. Expects a datetime instance with the time
		of starting the task. The text argument is optional.
		
		Note that the contents of the `current` file are overwritten.
		"""
		path = os.path.join(self.dir_path, 'current')
		line = [stamp.strftime(DT_FORMAT_FULL), text]
		
		with open(path, 'w') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(line)
		
		self.log.debug('Added an open log entry: '+str(line))
	
	
	def get_current(self, delete=False):
		"""
		Returns {stamp, text} of the currently open log entry or None if there
		is not such. The entry will be removed from the database file if the
		delete flag is set.
		"""
		path = os.path.join(self.dir_path, 'current')
		
		if not os.path.exists(path):
			return None
		
		entry = {'stamp': None, 'text': None}
		lines = []
		
		with open(path, 'r') as f:
			reader = csv.reader(f, delimiter='\t')
			for line in reader:
				lines.append(line)
		
		if len(lines) == 0:
			return None
		
		if len(lines) > 1:
			raise DatabaseError('Multiple current log entries found')
		
		try:
			entry['stamp'] = datetime.strptime(lines[0][0], DT_FORMAT_FULL)
		except ValueError as err:
			self.log.error(str(err))
			raise DatabaseError('Could not read the current db file')
		
		entry['text'] = lines[0][1] if lines[0][1] else ''
		
		if delete:
			with open(path, 'w') as f:
				pass
		
		return entry
	
	
	def add(self, stamp, action, text):
		"""
		Creates a new log entry.
		"""
		path = self._get_path(stamp.year, stamp.month, create=True)
		data = []
		
		if os.path.exists(path):
			with open(path) as f:
				reader = csv.reader(f, delimiter='\t')
				for line in f:
					data.append(line)
		
		data.append([
			
		])
		
		with open(path, 'w') as f:
			writer = csv.writer(f, delimiter='\t')
			for line in data:
				writer.writerow(line)
		
		self.log.debug('Added log entry: ')
	
	
	def get_day(self, year, month, day):
		"""
		Returns the set of logs for the given date.
		"""
		pass
	
	
	def get_month(self, year, month):
		"""
		Returns the set of logs for the given month.
		"""
		pass
	
	
	def get_year(self, year):
		"""
		Returns the set of logs for the given year.
		"""
		pass



