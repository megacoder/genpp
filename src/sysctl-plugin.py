#!/usr/bin/env python2
# vim: ai sm noet sw=4 ts=4

import	os
import	sys
import	math
import	superclass

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'sysctl-pp'
	DESCRIPTION="""Output /etc/sysctl.conf in canonical form."""

	def __init__( self ):
		super( PrettyPrint, self ).__init__()
		return

	def reset( self ):
		super( PrettyPrint, self ).reset()
		return

	def	pre_begin_file( self, name = None ):
		self.maxlen = 0
		self.lines  = list()
		return

	def ignore( self, name ):
		return not name.endswith( '.conf' )

	def next_line( self, line ):
		tokens = map(
			str.strip,
			# Drop comments, split by '=', trim whitespace
			line.split( '#', 1 )[ 0 ].split( '=', 1 )
		)
		if len( tokens ) == 2:
			key   = tokens[ 0 ]
			value = tokens[ 1 ]
			self.maxlen = max(
				self.maxlen,
				len( key ),
			)
			self.lines.append( [ key, value ] )
		return

	def report( self, final = False ):
		if not final:
			if len( self.lines ) == 0:
				self.println(  '# Empty' )
			else:
				fmt = '{{0:>{0}}} = {{1}}'.format( self.maxlen )
				for key,value in sorted(
					self.lines,
					key = lambda a : a[0].lower()
				):
					self.println( fmt.format( key, value ) )
		return
