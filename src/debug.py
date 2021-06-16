#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	__future__		import	print_function

import	os
import	sys
import	traceback

class	debugmode:

	def __init__( self, title ):
		self.title	 = title
		if self.title:
			print( '- entering {0}'.format( self.title ) )

	def __enter__( self ):
		return

	def __exit__( self, type, value, tb ):
		if type:
			print( '- left {0}'.format( self.title ) )
			raise type(value)
		return

if __name__ == '__main__':
	with debugmode( 'kind' ):
		print( 'benevolent' )
	with debugmode( 'fault' ):
		print( 'here goes' )
		raise ValueError('frallup')
