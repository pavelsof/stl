from datetime import datetime

import logging
import os



class DatabaseError(ValueError):
	"""
	Raised when writing or retrieving data fails.
	"""
	pass



class Database:
	"""
	Responsible for adding and retrieving log records.
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
		
		return os.path.join(year_dir, str(month).zfill(2))
	
	
	def add(self, stamp, action, text):
		"""
		Creates a new log entry.
		"""
		pass
	
	
	def get_current(self):
		"""
		Returns the set of log items that have a start but not an end.
		"""
		pass
	
	
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



