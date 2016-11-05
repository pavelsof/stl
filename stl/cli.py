import argparse

from stl.core import Core
from stl import __version__



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
		usage = 'stl [-v] [--dir DIR] subcommand'
		desc = (
			'stl is a simple time logger that enables you to '
			'keep tally of how many hours you have worked on this or that'
		)
		
		self.parser = argparse.ArgumentParser(usage=usage, description=desc)
		
		self.parser.add_argument('--version', action='version', version=__version__)
		self.parser.add_argument('-v', '--verbose', action='store_true',
			help='print debug info')
		self.parser.add_argument('--dir', help=(
			'set the directory where the data will be saved; '
			'defaults to ~/.config/stl or ~/.stl'))
		
		self.subparsers = self.parser.add_subparsers(dest='command',
			title='subcommands')
		
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
			task = ' '.join(args.task) if args.task else ''
			return core.start(task=task)
		
		usage = 'stl start [task]'
		desc = (
			'make a log that you are starting to work'
		)
		
		subp = self.subparsers.add_parser('start', usage=usage,
			description=desc, help=desc)
		
		subp.add_argument('task', nargs=argparse.REMAINDER,
			help='the task that you are about to start working on')
		
		subp.set_defaults(func=start)
	
	
	def _init_stop(self):
		"""
		Inits the subparser that handles the stop command.
		"""
		def stop(core, args):
			return core.stop()
		
		usage = 'stl stop'
		desc = (
			'make a log that you just stopped working'
		)
		
		subp = self.subparsers.add_parser('stop', usage=usage,
			description=desc, help=desc)
		
		subp.set_defaults(func=stop)
	
	
	def _init_switch(self):
		"""
		Inits the subparser that handles the switch command.
		"""
		def switch(core, args):
			task = ' '.join(args.task) if args.task else ''
			return core.switch(task=task)
		
		usage = 'stl switch [task]'
		desc = (
			'shortcut for stl stop && stl start; '
			'stop the current task and immediately start another one'
		)
		
		subp = self.subparsers.add_parser('switch', usage=usage,
			description=desc, help=desc[:desc.find(';')])
		
		subp.add_argument('task', nargs=argparse.REMAINDER,
			help='the task that you are about to start working on')
		
		subp.set_defaults(func=switch)
	
	
	def _init_status(self):
		"""
		Inits the subparser that handles the status/show command.
		"""
		def status(core, args):
			extra = None
			
			for key in ['day', 'week', 'month', 'year', 'span', 'task']:
				if getattr(args, key) is not None:
					extra = (key, ' '.join(getattr(args, key)))
					break
			
			return core.status(extra=extra)
		
		usage = (
			'stl (status|show) '
			'[-d ... | -w ... | -m ... | -y ... | -s ... | -t ...]'
		)
		desc = (
			'show a status report; '
			'when called without further arguments, '
			'it will tell you what you are doing now'
		)
		
		subp = self.subparsers.add_parser('status', aliases=['show'],
			usage=usage, description=desc, help=desc[:desc.find(';')])
		
		group = subp.add_mutually_exclusive_group()
		group.add_argument('-d', '--day', nargs=argparse.REMAINDER, help=(
			'report for the given day, '
			'e.g. 15 oct, 2016-10-15, today, yesterday; '
			'empty string defaults to today'))
		group.add_argument('-w', '--week', nargs=argparse.REMAINDER, help=(
			'report for the given week, '
			'possible values are this and last; '
			'empty string defaults to this week'))
		group.add_argument('-m', '--month', nargs=argparse.REMAINDER, help=(
			'report for the given month, '
			'e.g. oct, 10, 10 2016, this, last; '
			'empty string defaults to this month'))
		group.add_argument('-y', '--year', nargs=argparse.REMAINDER, help=(
			'report for the given year, '
			'e.g. 2016, this, last; '
			'empty string defaults to this year'))
		group.add_argument('-s', '--span', nargs=argparse.REMAINDER, help=(
			'report for the time span between two dates (inclusive), '
			'e.g. 15 25 oct, 15 sep 2016 25 oct 2016, 15 sep 25 oct; '
			'if you specify only one date, the second will be set to today; '
			'some restrictions: '
			'the second date (if such) cannot be less specific than the first '
			'and months cannot be numbers'))
		group.add_argument('-t', '--task', nargs=argparse.REMAINDER,
			help='report for the given task')
		
		subp.set_defaults(func=status)
	
	
	def _init_add(self):
		"""
		Inits the subparser that handles the add command.
		"""
		def add(core, args):
			return core.add(args.start, args.stop, args.task)
		
		usage = 'stl add start stop [task]'
		desc = (
			'directly add a log entry; '
			'you can also do this from python, take a look at '
			'stl.core.Core.add()'
		)
		
		subp = self.subparsers.add_parser('add', usage=usage,
			description=desc, help=desc[:desc.find(';')])
		
		subp.add_argument('start',
			help='when work on the task started; use %%Y-%%m-%%dT%%H:%%M')
		subp.add_argument('stop',
			help='when work on the task stopped; use %%Y-%%m-%%dT%%H:%%M')
		subp.add_argument('task', nargs='?', default='',
			help='the task being worked on; optional')
		
		subp.set_defaults(func=add)
	
	
	def _init_edit(self):
		"""
		Inits the subparser that handles the edit command.
		"""
		def edit(core, args):
			month = ' '.join(getattr(args, 'month', []))
			core.edit(month)
		
		usage = 'stl edit [month]'
		desc = (
			'lets you vim the right file'
		)
		
		subp = self.subparsers.add_parser('edit', usage=usage,
			description=desc, help=desc)
		
		subp.add_argument('month', nargs=argparse.REMAINDER,
			help='the month you want to edit, e.g. oct 2016')
		
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
		
		core = Core(dir_path=args.dir, verbose=args.verbose)
		
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



