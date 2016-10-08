import csv

from datetime import datetime

import logging
import os



"""
The str(f|p)time format used in the database files and the expected length of
the formatted strings.
"""
DT_FORMAT = '%Y-%m-%d %H:%M'
DT_FORMAT_LEN = 16



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
		year_dir = os.path.join(self.dir_path, str(year).zfill(4))
		
		if create and not os.path.exists(year_dir):
			try:
				os.mkdir(year_dir)
			except:
				raise DatabaseError('Could not create database subdir')
			else:
				self.log.debug('Created dir '+year_dir)
		
		return os.path.join(year_dir, str(month).zfill(2))
	
	
	def _sanitise_text(self, text):
		"""
		Prepares the given text for writing to a database file. Also, the NUL
		byte is removed as it breaks the csv reader.
		"""
		return text.replace('\0', '').strip()
	
	
	def _read_entry(self, line):
		"""
		De-serialises a raw closed log file line and returns {start, stop,
		tag}, the first two being naive datetime instances.
		"""
		try:
			assert len(line) == 3
			start = datetime.strptime(line[0], DT_FORMAT)
			stop = datetime.strptime(line[1], DT_FORMAT)
			tag = str(line[2])
		except (AssertionError, ValueError) as err:
			self.log.error(str(err))
			raise ValueError
		
		return {'start': start, 'stop': stop, 'tag': tag}
	
	
	def add_current(self, stamp, tag=''):
		"""
		Creates a new open log entry. Expects a datetime instance with the time
		of starting the task. The tag argument is optional.
		
		Note that the contents of the `current` file are overwritten.
		"""
		path = os.path.join(self.dir_path, 'current')
		
		entry = [
			stamp.strftime(DT_FORMAT).zfill(DT_FORMAT_LEN),
			self._sanitise_text(tag)
		]
		
		with open(path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(entry)
		
		self.log.debug('Added an open log entry: '+str(entry))
	
	
	def get_current(self, delete=False):
		"""
		Returns {stamp, tag} of the currently open log entry or None if there
		is not such. The entry will be removed from the database file if the
		delete flag is set.
		"""
		path = os.path.join(self.dir_path, 'current')
		
		if not os.path.exists(path):
			return None
		
		entry = {'stamp': None, 'tag': None}
		lines = []
		
		with open(path, 'r', newline='') as f:
			reader = csv.reader(f, delimiter='\t')
			for line in reader:
				lines.append(line)
		
		if len(lines) == 0:
			return None
		
		if len(lines) > 1:
			raise DatabaseError('Multiple current log entries found')
		
		try:
			entry['stamp'] = datetime.strptime(lines[0][0], DT_FORMAT)
		except ValueError as err:
			self.log.error(str(err))
			raise DatabaseError('Could not read the current db file')
		
		entry['tag'] = lines[0][1] if lines[0][1] else ''
		
		if delete:
			with open(path, 'w', newline='') as f:
				pass
		
		return entry
	
	
	def add_complete(self, start, stop, tag=''):
		"""
		Creates a new closed log entry. Expects two datetime instances, for
		when work on the task started and stopped, respectively. The tag
		argument is optional.
		"""
		entry = [
			start.strftime(DT_FORMAT).zfill(DT_FORMAT_LEN),
			stop.strftime(DT_FORMAT).zfill(DT_FORMAT_LEN),
			self._sanitise_text(tag)
		]
		
		path = self._get_path(start.year, start.month, create=True)
		data = []
		
		if os.path.exists(path):
			with open(path, 'r', newline='') as f:
				reader = csv.reader(f, delimiter='\t')
				for line in reader:
					data.append(line)
		
		data.append(entry)
		
		with open(path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			for line in data:
				writer.writerow(line)
		
		self.log.debug('Added log entry: '+str(entry))
	
	
	def get_month(self, year, month):
		"""
		Returns the [] of {start, stop, tag} for the closed log entries for the
		given month. The [] is sorted by the start datetime.
		"""
		path = self._get_path(year, month)
		
		if not os.path.exists(path):
			return []
		
		li = []
		
		with open(path, newline='') as f:
			reader = csv.reader(f, delimiter='\t')
			for line in reader:
				try:
					entry = self._read_entry(line)
				except ValueError:
					raise DatabaseError(
						'Could not read the file for '+str(year)+'.'+str(month))
				else:
					li.append(entry)
		
		return list(sorted(li, key=lambda d: d['start']))
	
	
	def get_day(self, year, month, day):
		"""
		Returns the [] of {start, stop, tag} for the closed log entries for the
		given date. The [] is sorted by the start datetime.
		"""
		return list(filter(lambda d: d['start'].day == day,
				self.get_month(year, month)))
	
	
	def get_year(self, year):
		"""
		Returns the [] of {start, stop, tag} for the closed log entries for the
		given year. The [] is sorted by the start datetime.
		"""
		return [item
			for month in range(1, 13)
			for item in self.get_month(year, month)]
	
	
	def get_tag(self, tag):
		"""
		Returns the [] of {start, stop, tag} for the closed log entries that
		have the given string as their last column. The [] is sorted by the
		start datetime.
		"""
		pass



