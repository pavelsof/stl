import os.path

from setuptools import setup, find_packages

from stl import __version__



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(BASE_DIR, 'README.rst')) as f:
	README = f.read()



setup(
	name = 'stltimelogger',
	version = __version__,
	
	description = 'cli time logger',
	long_description = README,
	
	url = 'https://github.com/pavelsof/stl',
	
	author = 'Pavel Sofroniev',
	author_email = 'pavelsof@gmail.com',
	
	license = 'MIT',
	
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only'
	],
	keywords = 'cli time logger',
	
	packages = find_packages(),
	install_requires = [],
	
	test_suite = 'stl.tests',
	tests_require = ['pytz', 'hypothesis >= 3.5'],
	
	entry_points = {
		'console_scripts': [
			'stl = stl.cli:main'
		]
	}
)
