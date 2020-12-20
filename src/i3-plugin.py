#!/usr/bin/python
# vim: sw=4 ts=4 noet nu norelativenumber

from	bunch	import	Bunch
import	shlex
import	os
import	sys
import	stat
from	superclass	import	MetaPrettyPrinter

class	PrettyPrint( MetaPrettyPrinter ):

	NAME = 'i3-pp'
	DESCRIPTION = """Display I3 configuration files in canonical format."""

	def	__init__( self ):
		super( PrettyPrint, self ).__init__()
		self.settings = dict()
		return

	def	pre_begin_file( self, name  ):
		self.infos = list()
		return

	def	next_line( self, line ):
		line = line.expandtabs()
		try:
			tokens = [
				x for x in shlex.split( line, comments = False, posix = False )
			]
			info = Bunch(
				action    = None,
				hotkey    = None,
				args      = list(),
				comment   = None,
				col0      = ( len( line ) and line[ 0 ] == '#' ),
				lineno    = self.get_lineno(),
				cleaned   = line.rstrip(),
			)
			for info.indent in range( len( info.cleaned ) ):
				if not info.cleaned[ info.indent ].isspace():
					break
			for i in range( len( tokens ) ):
				if tokens[ i ] == '#':
					info.comment = ' '.join( tokens[ i: ] )
					break
				if i == 0:
					info.action = tokens[ i ]
				elif i == 1:
					info.hotkey = tokens[ i ]
				else:
					info.args.append( tokens[ i ] )
			self.infos.append( info )
		except Exception as e:
			self.error(
				'{0} injestion error.'.format( line ),
				e
			)
			raise ValueError
		return

	def	report( self, final = False ):
		if not final:
			try:
				max_action = max(
					[ 7 ] +
					[ len( info.action ) for info in self.infos if
   info.action and not info.col0 ]
				)
				max_hotkey = max(
					[ 7 ] +
					[ len( info.hotkey ) for info in self.infos if info.hotkey
	  and not info.col0 ]
				)
				fmt = '{{0}}{{1:<{0}}} {{2:<{1}}}  {{2}}'.format(
					max_action,
					max_hotkey
				)
				for info in self.infos:
					if len( info.cleaned ) == 0:
						self.println()
						continue
					if info.col0:
						self.println( info.cleaned )
						continue
					required =  fmt.format(
						' ' * info.indent,
						info.action if info.action else '',
						info.hotkey if info.hotkey else '',
						' '.join( info.args ) if info.args else '',
					)
					if info.comment:
						output = '{0:<44} {1}'.format(
							required,
							info.comment
						)
					else:
						output = required
					self.println( output )
			except Exception as e:
				self.error( 'Report Error', e )
				raise ValueError
			pass
		return
