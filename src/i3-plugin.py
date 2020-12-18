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
		cleaned = line.expandtabs().strip()
		try:
			info = Bunch(
				action   = None,
				hotkey   = None,
				args     = list(),
				comment  = None,
				lineno   = self.get_lineno(),
				cleaned  = cleaned,
				Ncleaned = len( cleaned ),
				tokens   = [
					x for x in shlex.split(
						cleaned, comments = False, posix = False
					)
				],
			)
			info.Ntokens = len( info.tokens )
			for i in range( info.Ntokens ):
				if tokens[ i ] == '#':
					# Eat this and all remaining tokens
					info.comment = ' '.join( info.tokens[ i: ] )
					break
				if i == 0:
					info.action = info.tokens[ i ]
				elif i == 1:
					info.hotkey = info.tokens[ i ]
				else:
					info.args.append( info.tokens[ i ] )
			self.infos.append( info )
			pass
		except Exception, e:
			print '{0} injestion error:\n{1}'.format(
				line,
				e
			)
			raise e
		return

	def	fmt_info( self, info ):
		required =  self.fmt.format(
			info.action if info.action else '',
			info.hotkey if info.hotkey else '',
			' '.join( info.args ) if info.args else '',
		).strip()
		if info.comment:
			output = '{0:<44}  {1}'.format(
				required,
				info.comment
			).strip()
		else:
			output = required.strip()
		N = len( output )
		return output, N

	def	report( self, final = False ):
		if not final:
			try:
				max_action = max(
					[ 7 ] +
					[ len( info.action ) for info in self.infos if
   info.action and not info.empty ]
				)
				max_hotkey = max(
					[ 7 ] +
					[ len( info.hotkey ) for info in self.infos if info.hotkey
	  and not info.empty ]
				)
				self.fmt = '{{0:<{0}}} {{1:<{1}}}  {{2}}'.format(
					max_action,
					max_hotkey
				)
				indent    = 0
				lineno    = -1
				was_blank = False
				for info in self.infos:
					lineno += 1
					output, N = self.fmt_info( info )
					if N == 0 or output[ 0 ] == '#':
						if not was_blank and lineno:
							self.println()
						self.println(
							( ' ' * indent ) + output
						)
						was_blank = True
					else:
						if was_blank:
							self.println()
						if info.Ntokens and info.tokens[ -1 ] == '}':
							indent -= 1
						self.println( output )
						if info.Ntokens and info.tokens[ -1 ] == '{':
							indent += 1
						was_blank = False
			except Exception, e:
				print 'Report Error,\nLine: {0}, {1}'.format(
					info.lineno,
					e
				)
				raise( e )
			pass
		return
