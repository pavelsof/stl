from datetime import datetime, timedelta

import logging.config
import logging



class Core:
	
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
	
	
	def start(self):
		"""
		"""
		pass
	
	
	def stop(self):
		"""
		"""
		pass
	
	
	def status(self):
		"""
		"""
		pass



