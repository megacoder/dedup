#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	setuptools	import	setup

import	glob
import	os

NAME	= 'dedup'
VERSION = '0.0.0rc2'

with open( '{0}/version.py'.format( NAME ), 'w') as f:
	print >>f, 'Version="{0}"'.format( VERSION )

setup(
	name             =	NAME,
	version          =	VERSION,
	description      =	'Remove duplicate images, my way.',
	author           =	'Tommy Reynolds',
	author_email     =	'Tommy.Reynolds@MegaCoder.com',
	license          =	'MIT',
	url              =	'http://www.MegaCoder.com',
	long_description =	open('README.md').read(),
	packages         =	[ NAME ],
	entry_points = {
		'console_scripts' : [ 'dedup=dedup.cli:main' ],
	},
)
