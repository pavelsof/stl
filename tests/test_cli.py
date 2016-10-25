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
	def test_start(self, d):
		args = ['start']
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		if d['task']:
			args.append(d['task'])
		
		with patch.object(Core, 'start') as mock_start:
			self.cli.run(args)
			mock_start.assert_called_once_with(task=d['task'])
	
	
	@given(fixed_dictionaries({
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_stop(self, d):
		args = ['stop']
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		
		with patch.object(Core, 'stop') as mock_stop:
			self.cli.run(args)
			mock_stop.assert_called_once_with()
	
	
	@given(fixed_dictionaries({
			'task': text().filter(lambda t: not t.startswith('-')),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_switch(self, d):
		args = ['switch']
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		if d['task']:
			args.append(d['task'])
		
		with patch.object(Core, 'switch') as mock_switch:
			self.cli.run(args)
			mock_switch.assert_called_once_with(task=d['task'])
	
	
	@given(fixed_dictionaries({
			'command': sampled_from(['status', 'show']),
			'extra': one_of(
				tuples(just('day'),
					sampled_from(['-d', '--day']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				tuples(just('week'),
					sampled_from(['-w', '--week']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				tuples(just('month'),
					sampled_from(['-m', '--month']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				tuples(just('year'),
					sampled_from(['-y', '--year']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				tuples(just('span'),
					sampled_from(['-s', '--span']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				tuples(just('task'),
					sampled_from(['-t', '--task']),
					text(min_size=1).filter(lambda t: not t.startswith('-'))),
				just(None)),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_status(self, d):
		args = [d['command']]
		extra = None
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		if d['extra']:
			extra = (d['extra'][0], d['extra'][2],)
			args.extend([d['extra'][1], d['extra'][2]])
		
		with patch.object(Core, 'status') as mock_status:
			self.cli.run(args)
			mock_status.assert_called_once_with(extra=extra)
	
	
	@given(fixed_dictionaries({
			'start': text(min_size=1).filter(lambda t: not t.startswith('-')),
			'stop': text(min_size=1).filter(lambda t: not t.startswith('-')),
			'task': text().filter(lambda t: not t.startswith('-')),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_add(self, d):
		args = ['add', d['start'], d['stop']]
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		if d['task']:
			args.append(d['task'])
		
		with patch.object(Core, 'add') as mock_add:
			self.cli.run(args)
			mock_add.assert_called_once_with(d['start'], d['stop'], d['task'])
	
	
	@given(fixed_dictionaries({
			'month': text().filter(lambda t: not t.startswith('-')),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_edit(self, d):
		args = ['edit']
		
		if d['verbose']:
			args.insert(0, d['verbose'])
		if d['month']:
			args.append(d['month'])
		
		with patch.object(Core, 'edit') as mock_edit:
			self.cli.run(args)
			mock_edit.assert_called_once_with(d['month'])



