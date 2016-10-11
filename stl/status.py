from datetime import datetime, timedelta

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
	
	
	def get_month_info(self, year, month):
		"""
		Returns a human-readable string containing info about the work done
		during the given month.
		"""
		pass
	
	
	def get_week_info(self, year, week):
		"""
		Returns a human-readable string containing info about the work done
		during the given week.
		"""
		pass
	
	
	def get_day_info(self, year, month, day):
		"""
		Returns a human-readable string containing info about the work done
		during the given day.
		"""
		pass
	
	
	def get_task_info(self, task):
		"""
		Returns a human-readable string containing info about the hours worked
		on the given task.
		"""
		pass



