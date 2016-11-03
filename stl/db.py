import csv

from datetime import datetime

import logging
import os



"""
The str(f|p)time format used in the database files and the expected length of
the formatted strings.
"""
CURRENT_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
CURRENT_DT_FORMAT_LEN = 19

ARCHIVE_DT_FORMAT = '%Y-%m-%d %H:%M'
ARCHIVE_DT_FORMAT_LEN = 16



class DatabaseError(ValueError):
	"""
	Raised when writing or retrieving data files.
	"""
	pass



class Database:
	"""
	Handles adding and retrieving log entries. There are two types of log
	entries depending on whether the task is stopped (archive) or not
	(current). There can be only one current log entry at a time and it is kept
	in a single file named `current`. The archive log entries are kept
	separately, one file per month, grouped in directories by year.
	"""
	
	def __init__(self, dir_path):
		"""
		Constructor. The path should lead to a directory at stl's disposal for
		creating and editing files in.
		"""
		self.log = logging.getLogger(__name__)
		self.dir_path = dir_path
	
	
	def _sanitise_text(self, text):
		"""
		Prepares the given text for writing to a database file. Also, the NUL
		byte is removed as it breaks the csv reader.
		"""
		return text.replace('\0', '').strip()
	
	
	"""
	Methods handling the current log
	"""
	def add_current(self, stamp, task=''):
		"""
		Creates a new current log entry. Expects a datetime instance with the
		time of starting the task. The task argument is optional.
		
		Note that the contents of the `current` file are silently overwritten.
		"""
		path = os.path.join(self.dir_path, 'current')
		
		entry = [
			stamp.strftime(CURRENT_DT_FORMAT).zfill(CURRENT_DT_FORMAT_LEN),
			self._sanitise_text(task)
		]
		
		with open(path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow(entry)
		
		self.log.debug('Added an open log entry: '+str(entry))
	
	
	def get_current(self, delete=False):
		"""
		Returns {stamp, task} of the current log entry or None if there is not
		such. The entry will be removed from the database file if the delete
		flag is set.
		"""
		path = os.path.join(self.dir_path, 'current')
		
		if not os.path.exists(path):
			return None
		
		entry = {'stamp': None, 'task': None}
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
			entry['stamp'] = datetime.strptime(lines[0][0], CURRENT_DT_FORMAT)
		except ValueError as err:
			self.log.error(str(err))
			raise DatabaseError('Could not read the current db file')
		
		entry['task'] = lines[0][1] if lines[0][1] else ''
		
		if delete:
			with open(path, 'w', newline='') as f:
				pass
			self.log.debug('Deleted contents of the current db file')
		
		return entry
	
	
	"""
	Methods handling the archive logs
	"""
	def get_path(self, year, month, create=False):
		"""
		Returns the absolute path to the file containing the archive log
		entries for the given year and month.
		"""
		year_dir = os.path.join(self.dir_path, str(year).zfill(4))
		
		if create and not os.path.exists(year_dir):
			try:
				os.mkdir(year_dir)
			except Exception as err:
				self.log.error(str(err))
				raise DatabaseError('Could not create database subdir')
			else:
				self.log.debug('Created dir '+year_dir)
		
		return os.path.join(year_dir, str(month).zfill(2))
	
	
	def _read_entry(self, line):
		"""
		De-serialises a raw archive log file line and returns {start, stop,
		task}, the first two being naive datetime instances.
		"""
		try:
			assert len(line) == 3
			start = datetime.strptime(line[0], ARCHIVE_DT_FORMAT)
			stop = datetime.strptime(line[1], ARCHIVE_DT_FORMAT)
			task = str(line[2])
		except (AssertionError, ValueError) as err:
			self.log.error(str(err))
			raise ValueError
		
		return {'start': start, 'stop': stop, 'task': task}
	
	
	def _sort_lines(self, lines):
		"""
		Returns the given [] of archive log file lines but sorted by the start
		datetime. Note that the method expects and returns [] of [] of str.
		"""
		def sort_key_func(item):
			try:
				return datetime.strptime(item[0], ARCHIVE_DT_FORMAT)
			except ValueError as err:
				self.log.error(str(err))
				raise ValueError
		
		return list(sorted(lines, key=sort_key_func))
	
	
	def add_complete(self, start, stop, task='', append=True):
		"""
		Creates a new archive log entry. Expects two datetime instances, for
		when work on the task started and stopped, respectively. The task
		argument is optional.
		
		If append is True, then the new entry is appended to the end of the
		respective db file. Otherwise, it is sorted into the right place.
		"""
		entry = [
			start.strftime(ARCHIVE_DT_FORMAT).zfill(ARCHIVE_DT_FORMAT_LEN),
			stop.strftime(ARCHIVE_DT_FORMAT).zfill(ARCHIVE_DT_FORMAT_LEN),
			self._sanitise_text(task)
		]
		
		path = self.get_path(start.year, start.month, create=True)
		data = []
		
		if os.path.exists(path):
			with open(path, 'r', newline='') as f:
				reader = csv.reader(f, delimiter='\t')
				for line in reader:
					data.append(line)
		
		data.append(entry)
		
		if not append:
			try:
				data = self._sort_lines(data)
			except ValueError:
				message = 'Could not read the file for {}.{}'
				raise DatabaseError(message.format(start.year, start.month))
		
		with open(path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			for line in data:
				writer.writerow(line)
		
		self.log.debug('Added log entry: '+str(entry))
	
	
	def get_month(self, year, month):
		"""
		Returns the [] of {start, stop, task} for the archive log entries for
		the given month. The [] is sorted by the start datetime.
		"""
		path = self.get_path(year, month)
		
		if not os.path.exists(path):
			return []
		
		li = []
		
		with open(path, newline='') as f:
			reader = csv.reader(f, delimiter='\t')
			for line in reader:
				try:
					entry = self._read_entry(line)
				except ValueError:
					message = 'Could not read the file for {}.{}'
					raise DatabaseError(message.format(year, month))
				else:
					li.append(entry)
		
		return list(sorted(li, key=lambda d: d['start']))
	
	
	def get_day(self, year, month, day):
		"""
		Returns the [] of {start, stop, task} for the archive log entries for
		the given date. The [] is sorted by the start datetime.
		"""
		return list(filter(lambda d: d['start'].day == day,
				self.get_month(year, month)))
	
	
	def get_year(self, year):
		"""
		Returns the [] of {start, stop, task} for the archive log entries for
		the given year. The [] is sorted by the start datetime.
		"""
		return [item
			for month in range(1, 13)
			for item in self.get_month(year, month)]
	
	
	def get_span(self, start, end):
		"""
		Returns the [] of {start, stop, task} for the archive log entries
		started between the points in time specified by the given date
		instances, inclusive. The [] is sorted by the start datetime.
		"""
		if start.year == end.year and start.month == end.month:
			return [log for log in self.get_month(start.year, start.month)
				if log['start'].date() >= start and log['start'].date() <= end]
		
		logs = [log for log in self.get_month(start.year, start.month)
				if log['start'].date() >= start]
		
		year, month = int(start.year), int(start.month)
		while True:
			month += 1
			if month > 12:
				month = 1
				year += 1
			if year == end.year and month == end.month:
				break
			logs.extend(self.get_month(year, month))
		
		logs.extend([log for log in self.get_month(end.year, end.month)
					if log['start'].date() <= end])
		
		return logs
	
	
	"""
	Methods handling the tasks file
	"""
	def _read_tasks_file(self, path):
		"""
		Returns a [] of the csv-read lines of the given tasks file. Helper used
		by add_task, get_task, and check_month_tasks.
		"""
		lines = []
		
		if os.path.exists(path):
			with open(path, newline='') as f:
				reader = csv.reader(f, delimiter='\t')
				for line in reader:
					lines.append(line)
		
		return lines
	
	
	def add_task(self, task, year, month):
		"""
		Adds an entry in the tasks file for the given task for the given year
		and month. The file is unchanged if the (task, year, month) tuple is
		already recorded.
		"""
		task = self._sanitise_text(task)
		if not len(task):
			raise ValueError('Task cannot be an empty string')
		
		s = '{}-{:02}'.format(year, month)
		
		path = os.path.join(self.dir_path, 'tasks')
		lines = self._read_tasks_file(path)
		entry = [line[1] for line in lines if line[0] == task]
		
		if len(entry) == 0:
			lines.append([task, s])
			lines = sorted(lines, key=lambda x: x[0])
		elif len(entry) == 1:
			li = entry[0].split(',')
			if s in li:
				return
			
			li.append(s)
			lines = [
				[line[0], ','.join(li) if line[0] == task else line[1]]
				for line in lines
			]
		else:
			raise DatabaseError('Multiple entries for task {}'.format(task))
		
		with open(path, 'w', newline='') as f:
			writer = csv.writer(f, delimiter='\t')
			for line in lines:
				writer.writerow(line)
		
		self.log.debug('Added time entry for task {}: {}'.format(task, entry))
	
	
	def get_task(self, task):
		"""
		Returns the [] of (year, month) tuples for which the given task has
		archive log entries.
		"""
		task = self._sanitise_text(task)
		if not len(task):
			raise ValueError('Task cannot be an empty string')
		
		path = os.path.join(self.dir_path, 'tasks')
		lines = self._read_tasks_file(path)
		entry = [line[1] for line in lines if line[0] == task]
		
		if len(entry) == 0:
			return []
		elif len(entry) > 1:
			raise DatabaseError('Multiple entries for task {}'.format(task))
		
		li = []
		entry = entry[0].split(',')
		
		for item in entry:
			try:
				item = item.split('-')
				item = tuple([int(item[0]), int(item[1])])
			except (KeyError, ValueError) as err:
				self.log.error(str(err))
				raise DatabaseError('Could not read tasks file')
			li.append(item)
		
		return li
	
	
	def check_month_tasks(self, year, month):
		"""
		Ensures that the tasks file contains the given month for all the tasks
		that are worked on during that month.
		
		Does not ensure (yet) that the tasks file does not include a task
		pointing to the given month which task is not in the given month's
		archive file.
		"""
		s = '{}-{:02}'.format(year, month)
		
		tasks = [item['task']
				for item in self.get_month(year, month) if item['task']]
		
		lines = self._read_tasks_file(os.path.join(self.dir_path, 'tasks'))
		
		mods = []
		
		for task in tasks:
			try:
				line = [line for line in lines if line[0] == task][0][1]
			except IndexError:
				continue
			
			if line.find(s) < 0:
				mods.append(task)
		
		for mod in mods:
			self.add_task(mod, year, month)
		
		self.log.debug('Checked tasks for {}'.format(s))



