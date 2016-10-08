from datetime import datetime, timedelta

import logging.config
import logging
import os

from stl.db import DatabaseError, Database



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
		Configures the logging. The verbosity flag determines whether the min
		log level would be DEBUG or INFO.
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
	
	
	def status(self):
		"""
		Returns a string saying whether there is a current task and what it is.
		"""
		curr = self.db.get_current()
		s = ''
		
		if curr is None:
			s = 'Nothing to see here'
		else:
			if curr['task']:
				s += 'Task: '+curr['task']
			s += 'Started: '+str(curr['stamp'])
		
		return s
	
	
	def scan(self):
		"""
		"""
		pass



