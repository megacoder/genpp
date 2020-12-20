#!/usr/bin/python
# vim: noet sw=4 ts=4 nu

import	os
import	sys
import	string
import	superclass

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'tcpwrapper'
	DESCRIPTION="""Display /etc/hosts.* in conical style."""

	def __init__( self ):
		super( PrettyPrint, self ).__init__()
		return

	def	reset( self ):
		super( PrettyPrint, self ).reset()
		self._setup()
		return

	def	_setup( self ):
		self.widths  = dict()
		self.content = list()
		return

	def	next_file( self, name ):
		super( PrettyPrint, self ).next_file( name )
		self._setup()
		return

	def	end_file( self, name ):
		self._show()
		self._setup()
		return

	def	_show( self ):
		for (n,tokens) in self.content:
			line = ''
			prefix = ''
			for i in xrange( 0, n ):
				fmt = '%%s%%-d%s' % self.widths[i]
				line += fmt % (prefix, tokens[i])
				prefix = ' : '
			self.prinln( line )
		return

	def	next_line( self, line ):
		tokens = map(
			str.strip,
			line.split( '#', 1 )[ 0 ].split( ':' )
		)
		n = len(tokens)
		if n > 0:
			for i in range( n ):
				self.widths[ i ] = max(
					self.widths.get( i, 1 ),
					len( tokens[ i ] )
				)
			self.content.append( (n, tokens) )
		return

	def	finish( self ):
		self._show()
		return
