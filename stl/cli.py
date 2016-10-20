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
		self._init_switch()
		
		self._init_status()
		
		self._init_add()
		self._init_edit()
	
	
	def _init_start(self):
		"""
		Inits the subparser that handles the start command.
		"""
		def start(core, args):
			task = args.task if args.task else ''
			return core.start(task=task)
		
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
			return core.stop()
		
		subp = self.subparsers.add_parser('stop')
		subp.add_argument('task', nargs='?',
			help='the task you are about to stop working on')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=stop)
	
	
	def _init_switch(self):
		"""
		Inits the subparser that handles the switch command.
		"""
		def switch(core, args):
			task = args.task if args.task else ''
			return core.switch(task=task)
		
		subp = self.subparsers.add_parser('switch')
		subp.add_argument('task', nargs='?',
			help='the task that you are about to start working on')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=switch)
	
	
	def _init_status(self):
		"""
		Inits the subparser that handles the status/show command.
		"""
		def status(core, args):
			extra = None
			
			for key in ['day', 'month', 'task']:
				if getattr(args, key) is not None:
					extra = (key, ' '.join(getattr(args, key)))
					break
			
			return core.status(extra=extra)
		
		subp = self.subparsers.add_parser('status', aliases=['show'])
		
		group = subp.add_mutually_exclusive_group()
		group.add_argument('-d', '--day', nargs='*')
		group.add_argument('-m', '--month', nargs='*')
		group.add_argument('-t', '--task', nargs=1)
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=status)
	
	
	def _init_add(self):
		"""
		Inits the subparser that handles the add command.
		"""
		def add(core, args):
			return core.add(args.start, args.stop, args.task)
		
		subp = self.subparsers.add_parser('add',
			description='adds a time log')
		
		subp.add_argument('start',
			help='when work on the task started; use %%Y-%%m-%%dT%%H:%%M')
		subp.add_argument('stop',
			help='when work on the task stopped; use %%Y-%%m-%%dT%%H:%%M')
		subp.add_argument('task', nargs='?', default='',
			help='the task being worked on; optional')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=add)
	
	
	def _init_edit(self):
		"""
		Inits the subparser that handles the edit command.
		"""
		def edit(core, args):
			month = ' '.join(getattr(args, 'month', []))
			core.edit(month)
		
		subp = self.subparsers.add_parser('edit',
			description='lets you vim the right file')
		
		subp.add_argument('month', nargs='*',
			help='the month you want to edit, e.g. oct 2016')
		
		subp.add_argument('-v', '--verbose', action='store_true')
		subp.set_defaults(func=edit)
	
	
	def run(self, raw_args=None):
		"""
		Parses the given arguments (or, except for in unit testing, sys.argv),
		inits the Core instance and transfers to that. Note that if raw_args is
		None, then argparse's parser defaults to reading sys.argv.
		
		Returns a human-readable string to be printed to the user.
		"""
		args = self.parser.parse_args(raw_args)
		
		if args.command is None:
			return self.parser.format_help()
		
		core = Core(verbose=args.verbose)
		
		try:
			res = args.func(core, args)
		except Exception as err:
			return str(err)
		
		return res



def main():
	"""
	The (only) entry point for the command-line interface as registered in
	setup.py. Inits a Cli instance, runs it with sys.argv, and prints the
	output to stdout.
	"""
	cli = Cli()
	res = cli.run()
	if res: print(res.strip())



