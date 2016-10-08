import argparse

from stl.core import Core



def main():
	"""
	The entry point for the command-line interface.
	"""
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	
	parser_start = subparsers.add_parser('start')
	parser_start.add_argument('task', nargs='?',
		help='the task that you are about to start working on')
	parser_start.add_argument('-v', '--verbose', action='store_true')
	parser_start.set_defaults(func='start')
	
	parser_stop = subparsers.add_parser('stop')
	parser_stop.add_argument('task', nargs='?',
		help='the task you are about to stop working on')
	parser_stop.add_argument('-v', '--verbose', action='store_true')
	parser_stop.set_defaults(func='stop')
	
	args = parser.parse_args()
	if 'func' not in args:
		parser.print_help()
	
	core = Core()
	
	try:
		res = getattr(core, args.func)()
	except Exception as err:
		print(str(err))
	else:
		if res:
			print(res)



