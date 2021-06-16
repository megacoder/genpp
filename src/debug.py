#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	__future__		import	print_function

import	os
import	sys
import	traceback

class	debugmode:

	def __init__( self, title, cascade = False, file = sys.stderr ):
		self.title   = title
		self.cascade = cascade
		self.file    = file

	def __enter__( self ):
		return

	def __exit__( self, type, value, tb ):
		if type:
			print( self.title, file = self.file )
			if self.cascade:
				raise type(value)
		return

if __name__ == '__main__':
	with debugmode( 'kind' ):
		print( 'benevolent' )
	with debugmode( 'fault' ):
		print( 'here goes' )
		raise ValueError( '***FAULT***' )
	with debugmode( 'fault', True ):
		print( 'bottom of the barrel' )
		raise ValueError( '***FIRSTFAULT***' )
