from datetime import datetime, timedelta

import logging.config
import logging
import os

from stl.db import DatabaseError, Database
from stl.status import Status
from stl.time import prettify_delta



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
	
	
	def start(self, task=''):
		"""
		Adds a record that work is starting on the given task. The latter can
		also be an empty string. Raises ValueError if there is already a
		current task.
		"""
		curr = self.db.get_current()
		if curr is not None:
			raise ValueError('You are already working on something')
		
		self.db.add_current(datetime.now(), task)
	
	
	def stop(self):
		"""
		Adds a record that work has stopped on the current task. Raises
		ValueError if there is not a current task.
		"""
		curr = self.db.get_current(delete=True)
		
		if curr is None:
			raise ValueError('You are not working on anything')
		
		self.db.add_complete(curr['stamp'], datetime.now(), curr['task'])
		
		try:
			self.db.add_task(curr['task'], curr['stamp'].year, curr['stamp'].month)
		except ValueError:
			pass
	
	
	def status(self, extra=None):
		"""
		Returns a human-readable string with status information. The optional
		argument can be a (key, value) tuple, with the key being one of ('day',
		'week', 'month', 'task').
		"""
		status = Status(self.db)
		
		if extra:
			key, value = extra
			if key == 'day':
				now = datetime.now()
				res = status.get_day_info(now.year, now.month, now.day)
			elif key == 'month':
				now = datetime.now()
				res = status.get_month_info(now.year, now.month)
			else:
				res = status.get_task_info(value)
		else:
			res = status.get_current_info(datetime.now())
		
		return res
	
	
	def scan(self):
		"""
		"""
		pass



