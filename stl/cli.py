import argparse



def start(args):
	"""
	The entry point for the start sub-command.
	"""
	print('start')



def stop(args):
	"""
	The entry point for the stop sub-command.
	"""
	print('stop')



def main():
	"""
	The entry point for the command-line interface.
	"""
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	
	parser_start = subparsers.add_parser('start')
	parser_start.add_argument('task', nargs='?',
		help='the task that you are about to start working on')
	parser_start.set_defaults(func=start)
	
	parser_stop = subparsers.add_parser('stop')
	parser_stop.add_argument('task', nargs='?',
		help='the task you are about to stop working on')
	parser_stop.set_defaults(func=stop)
	
	args = parser.parse_args()
	if 'func' in args:
		args.func(args)
	else:
		parser.print_help()



