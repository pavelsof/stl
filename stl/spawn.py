import logging
import os
import shutil
import subprocess


"""
If echo $EDITOR is None, these will be tried in order.
"""
FALLBACK_EDITORS = ['vim', 'vi']



class SpawnError(ValueError):
	"""
	Raised when there is a problem with calling an external programme.
	"""
	pass



class Spawner:
	"""
	Holds methods for running external programmes.
	"""
	
	def __init__(self):
		"""
		Constructor. Inits the logging facility.
		"""
		self.log = logging.getLogger(__name__)
	
	
	def _get_editor(self):
		"""
		Returns the command that invokes the user's (hopefully) favourite
		editor. If there is no environment variable $EDITOR, it tries some
		fallbacks. If that fails, a SpawnError is raised.
		"""
		if 'EDITOR' in os.environ:
			return os.environ['EDITOR']
		
		for editor in FALLBACK_EDITORS:
			if shutil.which(editor):
				return editor
		
		raise SpawnError('Could not find an editor')
	
	
	def edit(self, file_path):
		"""
		Opens the given file with the user's favourite editor. It is a blocking
		method, it will only return after the user is done editing.
		"""
		args = [self._get_editor(), os.path.abspath(file_path)]
		
		try:
			subprocess.run(args, check=True)
		except OSError as err:
			self.log.error(str(err))
			raise SpawnError('Could not run {}'.format(args[0]))
		except subprocess.CalledProcessError as err:
			self.log.error(str(err))
			raise SpawnError('Could not close {} normally'.format(args[0]))



