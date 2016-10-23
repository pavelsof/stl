from datetime import datetime, timedelta
from functools import reduce

import logging

from stl.time import prettify_date, prettify_datetime, prettify_delta



class Status:
	"""
	Represents an answer to an inquiry about the status. Knows what comprises
	different status informations.
	
	Methods of this class only call the Database.get_* methods, i.e.
	information from the database is only retrieved, not altered.
	"""
	
	def __init__(self, db):
		"""
		Constructor.
		"""
		self.db = db
		self.log = logging.getLogger(__name__)
	
	
	def get_current_info(self, now):
		"""
		Returns a human-readable string with info about the current task, if
		such. Does not check the time itself and expects a datetime instance.
		"""
		curr = self.db.get_current()
		if curr is None:
			return 'nothing to see here'
		
		li = []
		
		if curr['task']:
			li.append('task: {}'.format(curr['task']))
		
		delta = now - curr['stamp']
		
		li.append('started: {}'.format(curr['stamp']))
		li.append('elapsed: {}'.format(prettify_delta(delta)))
		
		return '\n'.join(li)
	
	
	def _get_time_info(self, logs):
		"""
		Helper used by the following three methods. Returns a human-readable
		string containing info about the time spent working based on the given
		log entries.
		"""
		hours = timedelta(0)
		tasks = {}  # task: timedelta
		
		for entry in logs:
			delta = entry['stop'] - entry['start']
			hours += delta
			if len(entry['task']):
				if entry['task'] in tasks:
					tasks[entry['task']] += delta
				else:
					tasks[entry['task']] = delta
		
		tasks = [(task, delta) for task, delta in tasks.items()]
		tasks = sorted(tasks, key=lambda x: x[1])
		tasks = ', '.join([
			'{} ({})'.format(task, prettify_delta(delta))
			for task, delta in tasks
		])
		
		if not tasks: tasks = '-'
		
		return '\n'.join([
			'tasks: {}'.format(tasks),
			'total: {}'.format(prettify_delta(hours))
		])
	
	
	def get_day_info(self, year, month, day):
		"""
		Returns a human-readable string containing info about the work done
		during the given day.
		"""
		logs = self.db.get_day(year, month, day)
		return '\n'.join([
			'[{}]'.format(prettify_date(year, month, day)),
			self._get_time_info(logs)
		])
	
	
	def get_week_info(self, monday, sunday):
		"""
		Returns a human-readable string containing info about the work done
		during the week defined by the given date instances.
		"""
		logs = self.db.get_span(monday, sunday)
		
		pretty_monday = prettify_date(monday.year, monday.month, monday.day)
		pretty_sunday = prettify_date(sunday.year, sunday.month, sunday.day)
		
		return '\n'.join([
			'[{} to {}]'.format(pretty_monday, pretty_sunday),
			self._get_time_info(logs)
		])
	
	
	def get_month_info(self, year, month):
		"""
		Returns a human-readable string containing info about the work done
		during the given month.
		"""
		logs = self.db.get_month(year, month)
		return '\n'.join([
			'[{}]'.format(prettify_date(year, month)),
			self._get_time_info(logs)
		])
	
	
	def get_year_info(self, year):
		"""
		Returns a human-readable string containing info about the work done
		during the given year.
		"""
		logs = self.db.get_year(year)
		return '\n'.join([
			'[{}]'.format(year),
			self._get_time_info(logs)
		])
	
	
	def get_task_info(self, task):
		"""
		Returns a human-readable string containing info about the hours worked
		on the given task.
		"""
		logs = []
		for year, month in self.db.get_task(task):
			logs.extend(list(filter(
				lambda entry: entry['task'] == task,
				self.db.get_month(year, month))))
		
		if not len(logs):
			return 'task {} not found'.format(task)
		
		logs = list(sorted(logs, key=lambda item: item['start']))
		
		started = logs[0]['start']
		last_mod = logs[-1]['stop']
		hours = reduce(lambda x,y: x+y,
					[log['stop']-log['start'] for log in logs])
		
		return '\n'.join([
			'[{}]'.format(task),
			'started: {}'.format(prettify_datetime(started)),
			'last mod: {}'.format(prettify_datetime(last_mod)),
			'total: {}'.format(prettify_delta(hours))
		])



