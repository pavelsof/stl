import subprocess

from unittest.mock import patch
from unittest import TestCase

from stl.spawn import Spawner



class SpawnerTestCase(TestCase):
	
	def setUp(self):
		self.spawner = Spawner()
	
	def test_edit(self):
		with patch.object(subprocess, 'run') as mock_run:
			self.spawner.edit('EATME')
			self.assertEqual(mock_run.call_count, 1)



