from datetime import datetime, timedelta

import logging.config
import logging
import os

from stl.db import DatabaseError, Database
from stl.status import Status
from stl.time import Parser, prettify_delta



"""
The default logging configuration to be used; it will be slightly altered if
the verbose flag is set (see Core.__init__).
"""
DEFAULT_LOGGING = {
	'version': 1,
	'formatters': {
		'simple': {
			'format': '%(message)s'
		}
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
			'level': logging.DEBUG,
			'formatter': 'simple'
		}
	},
	'root': {
		'handlers': ['console'],
		'level': logging.INFO
	}
}



class Core:
	"""
	The controller singleton. This is what stays behind the cli and manipulates
	the other modules in order to accomplish the tasks requested by the user.
	"""
	
	def __init__(self, verbose=False):
		"""
		Constructor. Configures the logging and inits the Database instance.
		
		The verbosity flag determines whether the min log level would be DEBUG
		or INFO.
		"""
		config = dict(DEFAULT_LOGGING)
		
		if verbose:
			config['root']['level'] = logging.DEBUG
		
		logging.config.dictConfig(config)
		
		self.log = logging.getLogger(__name__)
		
		self.dir_path = self._get_dir_path()
		self.db = Database(self.dir_path)
	
	
	def _get_dir_path(self):
		"""
		Returns the path to the dir that contains the database files, either
		~/.config/stl or ~/.stl. If none exists, one will be created.
		"""
		for dir_path in ('~/.config/stl', '~/.stl'):
			dir_path = os.path.expanduser(dir_path)
			if os.path.exists(dir_path) and os.path.isdir(dir_path):
				return dir_path
		
		config_path = os.path.expanduser('~/.config')
		if os.path.exists(config_path) and os.path.isdir(config_path):
			dir_path = os.path.join(config_path, 'stl')
		else:
			dir_path = os.path.expanduser('~/.stl')
		
		try:
			os.mkdir(dir_path)
		except Exception as err:
			self.log.error(str(err))
			raise ValueError('Could not create database directory')
		else:
			self.log.debug('Created '+str(dir_path))
		
		return dir_path
	
	
	def start(self, task='', now=None):
		"""
		Adds a record that work is starting on the given task. The latter can
		also be an empty string. Raises ValueError if there is already a
		current task.
		"""
		if now is None:
			now = datetime.now()
		
		curr = self.db.get_current()
		if curr is not None:
			raise ValueError('You are already working on something')
		
		self.db.add_current(now, task)
		
		s = 'started'
		if task:
			s += ' on '+task
		
		return s
	
	
	def stop(self, now=None):
		"""
		Adds a record that work has stopped on the current task. Raises
		ValueError if there is not a current task.
		"""
		if now is None:
			now = datetime.now()
		
		curr = self.db.get_current(delete=True)
		
		if curr is None:
			raise ValueError('You are not working on anything')
		
		self.db.add_complete(curr['stamp'], now, curr['task'])
		
		try:
			self.db.add_task(curr['task'], curr['stamp'].year, curr['stamp'].month)
		except ValueError:
			pass
		
		s = 'stopped'
		if curr['task']:
			s += ' with '+curr['task']
		
		return s
	
	
	def switch(self, task='', now=None):
		"""
		Shortcut that stops the current task and immediately starts a new one.
		"""
		res_stop = self.stop(now=now)
		res_start = self.start(task, now=now)
		
		return '\n'.join([res_stop, res_start])
	
	
	def status(self, extra=None, now=None):
		"""
		Returns a human-readable string with status information. The optional
		argument can be a (key, value) tuple, with the key being one of ('day',
		'week', 'month', 'task').
		"""
		if now is None:
			now = datetime.now()
		
		status = Status(self.db)
		
		if not extra:
			return status.get_current_info(now)
		
		key, value = extra
		
		if key == 'task':
			return status.get_task_info(value)
		
		parser = Parser(now)
		if key == 'day':
			year, month, day = parser.extract_date(value)
			return status.get_day_info(year, month, day)
		elif key == 'month':
			year, month = parser.extract_month(value)
			return status.get_month_info(year, month)



