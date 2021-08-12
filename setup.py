#!/usr/bin/env python
# vim: noet sw=4 ts=4 ai sm ff=unix norelativenumber nu

from	setuptools	import	setup

import	glob
import	os

NAME	= 'genpp'
VERSION = '1.1.16'

with open( '{0}/version.py'.format( 'src' ), 'w') as f:
	print(
		'Version="{0}"'.format( VERSION ),
		file = f
	)

setup(
	name			 =	NAME,
	version			 =	VERSION,
	description		 =	'Generic Pretty Printer, using plugins',
	author			 =	'Tommy Reynolds',
	author_email	 =	'Tommy.Reynolds@MegaCoder.com',
	license			 =	'MIT',
	url				 =	'http://www.MegaCoder.com',
	long_description =	open('README.md').read(),
	packages		 =	[ 'genpp' ],
	package_dir		 =	{
			'genpp': 'src'
	},
	scripts			 =	{
		"scripts/genpp",
	},
)
