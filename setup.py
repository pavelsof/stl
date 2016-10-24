import os.path

from setuptools import setup, find_packages



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(BASE_DIR, 'README.md')) as f:
	README = f.read()



setup(
	name = 'stltimelogger',
	version = '0.0',
	
	description = 'Yet another cli time logger',
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
	
	test_suite = 'tests',
	tests_require = ['pytz', 'hypothesis >= 3.5'],
	
	entry_points = {
		'console_scripts': [
			'stl = stl.cli:main'
		]
	}
)
