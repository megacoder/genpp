#!/usr/bin/env python2
# vim: sw=4 ts=4 noet

import	os
import	sys
import	stat
from	superclass	import	MetaPrettyPrinter

class	PrettyPrint( MetaPrettyPrinter ):

	NAME = 'ocfs2-pp'
	DESCRIPTION = """Display Oracle OCFS2 configuration files in canonical
	format."""

	def	__init__( self ):
		super( PrettyPrint, self ).__init__()
		return

	def	pre_begin_file( self, fn = None ):
		self.stanzas = dict()
		self.key     = None
		self.stanza  = dict()
		return

	def	next_line( self, line ):
		line = line.split( '#', 1 )[0].strip()
		if line.endswith( ':' ):
			if self.stanza:
				self.stanzas.append( self.stanza )
				self.stanzas[ self.key ] = self.stanza
			self.key    = line[:-1]
			self.stanza = dict()
		else:
			tokens = map(
				str.strip,
				line.split( '=', 1 )
			)
			if len(tokens) == 2:
				self.stanza[ tokens[ 0 ], tokens[ 1 ] ]
		return

	def	post_end_file( self, fn = None ):
		if len( self.stanza.keys() ):
			self.stanzas[ self.key] = self.stanza
		self.report()
		return

	def	report( self, final = False ):
		if not final:
			for i,key in enumerate( sorted( self.stanzas.keys() ) ):
				if i:
					self.println()
				self.title(
					'{0}:'.formt( key )
				)
				stanza = self.stanzas[ key ]
				N = max(
					map(
						len,
						stanza.keys()
					)
				)
				fmt = '{{0:<{0}}} {{1}}'
				for name in sorted( stanza.keys() ):
					self.println(
						fmt.format(
							name,
							stanza[ name ]
						)
					)
		return
