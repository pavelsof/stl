import argparse

from stl.core import Core



class Cli:
	"""
	Singleton that handles the user input, inits the whole machinery, and takes
	care of exiting the programme.
	"""
	
	def __init__(self):
		"""
		Constructor. Inits the argparse parser and then all the subparsers
		through the _init_* methods.
		
		Each of the latter defines a function that takes a Core instance and
		the argparse args as arguments, which function will be called if the
		respective command is called.
		"""
		self.parser = argparse.ArgumentParser()
		self.subparsers = self.parser.add_subparsers(dest='command')
		
		self._init_start()
		self._init_stop()
		self._init_status()
	
	
	def _init_start(self):
		"""
		Inits the subparser that handles the start command.
		"""
		def start(core, args):
			task = args.task if args.task else ''
			core.start(task=task)
		
		subp = self.subparsers.add_parser('start')
		subp.add_argument('task', nargs='?',
			help='the task that you are about to start working on')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=start)
	
	
	def _init_stop(self):
		"""
		Inits the subparser that handles the stop command.
		"""
		def stop(core, args):
			core.stop()
		
		subp = self.subparsers.add_parser('stop')
		subp.add_argument('task', nargs='?',
			help='the task you are about to stop working on')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=stop)
	
	
	def _init_status(self):
		"""
		Inits the subparser that handles the status command.
		"""
		def status(core, args):
			return core.status()
		
		subp = self.subparsers.add_parser('status', aliases=['show'])
		
		'''subp.add_argument('-d', '--day')
		subp.add_argument('-w', '--week')
		subp.add_argument('-m', '--month')
		
		subp.add_argument('-t', '--task')'''
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=status)
	
	
	def parse_args(self, raw_args=None):
		"""
		Parses the given arguments (or, except for in unit testing, sys.argv),
		inits the Core instance and transfers to that. Note that if raw_args is
		None, then argparse's parser defaults to reading sys.argv.
		
		Returns True/False indicating whether the run was successful.
		"""
		args = self.parser.parse_args(raw_args)
		
		if 'command' not in args:
			self.parser.print_help()
			return True
		
		core = Core(verbose=args.verbose)
		
		try:
			res = args.func(core, args)
		except Exception as err:
			print(str(err))
			return False
		
		if res:
			print(res)
		
		return True



def main():
	"""
	The (only) entry point for the command-line interface as registered in
	setup.py. Inits a Cli instance and parses sys.argv.
	"""
	cli = Cli()
	cli.parse_args()



