#!/usr/bin/python
# vim: noet sw=4 ts=4

import	os
import	sys
import	superclass
import	align
import	shlex

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME        = 'rsyslog-pp'
	DESCRIPTION = """Display rsyslog files in canonical style."""

	def	__init__( self ):
		super( PrettyPrint, self ).__init__()
		return

	def pre_begin_file( self ):
		self.vars = []
		self.settings = align.Align( titles = 1 )
		self.settings.add([
			'# NAME',
			'VALUE',
		])
		alignment = 'll'
		self.settings.set_title_alignment( alignment )
		self.settings.set_alignment( alignment )
		#
		self.actions = align.Align( titles = 1 )
		self.actions.add([
			'# ID',
			'ACTION'
		])
		alignment = 'rl'
		self.actions.set_title_alignment( alignment )
		self.actions.set_alignment( alignment )
		return

	def	next_line( self, line ):
		line = line.split( '#', 1 )[0].strip()
		if line.startswith( '$' ):
			tokens = [
				x for x in map(
					str.strip,
					shlex.split(
						line,
						comments = True,
						posix    = True,
						shell    = False
					)
				)
			]
			if len( tokens ) >= 2 and len( tokens[ 0 ] ):
				self.settings.add( tokens )
		else:
			tokens = [
				x for x in map(
					str.strip,
					shlex.split(
						line,
						comments = True,
						posix    = True,
						shell    = False
					)
				)
			]
			if len( tokens ):
				self.actions.add( tokens )
		return

	def	report( self, final = False ):
		if not final:
			for line in self.settings.get_items():
				self.println( ' '.join( line ) )
			if len(self.actions) > 1:
				self.println()
			for i,action in iterate( self.actions.get_items() ):
				self.println(
					'{0:2d}'.format(
						i + 1,
						' '.join( action )
					)
				)
		return

# Minimal skeleton for testing individual modules

if __name__ == '__main__':
	fn = '<selftest>'
	pp = PrettyPrint()
	pp.pre_begin_file()
	pp.begin_file( fn )
	with open( '/etc/rsyslog.conf' ) as f:
		for linein f.readlines():
			pp.next_line( line )
	pp.end_file( fn )
	pp.post_end_file()
	pp.report( final = True )

