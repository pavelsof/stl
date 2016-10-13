from unittest.mock import patch
from unittest import TestCase

from hypothesis.strategies import fixed_dictionaries, just, one_of
from hypothesis.strategies import sampled_from, text, tuples
from hypothesis import given

from stl.cli import Cli
from stl.core import Core



class CliTestCase(TestCase):
	
	def setUp(self):
		self.cli = Cli()
	
	
	@given(fixed_dictionaries({
			'task': text().filter(lambda t: not t.startswith('-')),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_start_does_not_break(self, d):
		args = [value for value in d.values() if value]
		
		with patch.object(Core, 'start') as mock_start:
			self.cli.run(['start'] + args)
			mock_start.assert_called_once_with(task=d['task'])
	
	
	@given(fixed_dictionaries({
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_stop_does_not_break(self, d):
		args = [value for value in d.values() if value]
		
		with patch.object(Core, 'stop') as mock_stop:
			self.cli.run(['stop'] + args)
			mock_stop.assert_called_once_with()
	
	
	@given(fixed_dictionaries({
			'command': sampled_from(['status', 'show']),
			'extra': one_of(
				tuples(just('day'), sampled_from(['-d', '--day']), text(min_size=1)),
				tuples(just('month'), sampled_from(['-m', '--month']), text(min_size=1)),
				tuples(just('task'),
					sampled_from(['-t', '--task']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				just(None)),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_status_does_not_break(self, d):
		args, extra = [], None
		if d['extra']:
			extra = (d['extra'][0], d['extra'][2],)
			args.extend([d['extra'][1], d['extra'][2]])
		if d['verbose']:
			args.append(d['verbose'])
		
		with patch.object(Core, 'status') as mock_status:
			self.cli.run([d['command']] + args)
			mock_status.assert_called_once_with(extra=extra)



