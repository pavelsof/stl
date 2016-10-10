from unittest.mock import patch
from unittest import TestCase

from hypothesis.strategies import fixed_dictionaries, sampled_from, text
from hypothesis import given

from stl.cli import Cli
from stl.core import Core



class CliTestCase(TestCase):
	
	def setUp(self):
		self.cli = Cli()
	
	
	@given(fixed_dictionaries({
			'task': text(),
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_start_does_not_break(self, d):
		args = [value for value in d.values() if value]
		
		with patch.object(Core, 'start') as mock_start:
			self.assertTrue(self.cli.parse_args(['start'] + args))
			mock_start.assert_called_once_with(task=d['task'])
	
	
	@given(fixed_dictionaries({
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def test_stop_does_not_break(self, d):
		args = [value for value in d.values() if value]
		
		with patch.object(Core, 'stop') as mock_stop:
			self.assertTrue(self.cli.parse_args(['stop'] + args))
			mock_stop.assert_called_once_with()
	
	
	@given(fixed_dictionaries({
			'verbose': sampled_from(['-v', '--verbose', ''])}))
	def untest_status_does_not_break(self, d):
		args = [value for value in d.values() if value]
		
		with patch.object(Core, 'status') as mock_status:
			self.assertTrue(self.cli.parse_args(['status'] + args))
			mock_status.assert_called_once_with()



