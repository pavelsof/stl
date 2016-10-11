from datetime import timedelta
from functools import reduce

import logging

from stl.utils import get_natural_str



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
			return ''
		
		li = []
		
		if curr['task']:
			li.append('task: {}'.format(curr['task']))
		
		delta = now - curr['stamp']
		
		li.append('started: {}'.format(curr['stamp']))
		li.append('elapsed: {}'.format(get_natural_str(delta)))
		
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
			'{} ({})'.format(task, get_natural_str(delta))
			for task, delta in tasks
		])
		
		return '\n'.join([
			'tasks: {}'.format(tasks),
			'total: {}'.format(get_natural_str(hours))
		])
	
	
	def get_day_info(self, year, month, day):
		"""
		Returns a human-readable string containing info about the work done
		during the given day.
		"""
		return self._get_time_info(self.db.get_day(year, month, day))
	
	
	def get_week_info(self, year, week):
		"""
		Returns a human-readable string containing info about the work done
		during the given week.
		"""
		pass
	
	
	def get_month_info(self, year, month):
		"""
		Returns a human-readable string containing info about the work done
		during the given month.
		"""
		return self._get_time_info(self.db.get_month(year, month))
	
	
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
			'started: {}'.format(started),
			'last mod: {}'.format(last_mod),
			'total: {}'.format(get_natural_str(hours))
		])



