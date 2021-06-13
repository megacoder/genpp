#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	__future__	import print_function

import	os
import	sys
import	glob
import	traceback

class	MetaPrettyPrinter( object ):

	"""
		Populate this!
	"""

	NAME		= 'superclass'
	DESCRIPTION = 'Man behind the curtain.'
	USAGE		= None
	GLOB		= '*'
	HELPFMT		= '%23s | %s'

	def __init__( self ):
		self.reset()
		return

	def reset( self ):
		self.sc_out			 = sys.stdout
		self.sc_fileno		 = 0
		self.sc_lineno		 = 0
		self.sc_filename	 = '{stdin}'
		self.sc_multi		 = 0
		self.sc_do_backslash = None
		self.sc_footnotes	 = []
		self.linesout_enable( False )
		return

	def	linesout_enable( self, enabled = True ):
		self.sc_linesout = enabled
		if enabled:
			self.sc_linesoutn = 0
		return

	def	showing_linesout( self ):
		return self.sc_linesout

	def	get_linesout( self, bump = True ):
		if bump:
			self.sc_linesoutn += 1
		return self.sc_linesoutn

	def get_lineno( self ):
		return self.sc_lineno

	def get_out( self ):
		return self.sc_out

	def get_fileno( self ):
		return self.sc_fileno

	def get_filename( self ):
		return self.sc_filename

	def get_multi( self ):
		return self.multi

	def get_backslash( self ):
		return self.sc_do_backlash

	def own_glob( self ):
		try:
			pattern = self.GLOB
			if pattern == '-':
				retval = '-'
			else:
				retval = glob.glob( pattern )
		except Exception as e:
			retval = [ '-' ]
		return retval

	def advise( self, names = [ '-' ] ):
		self.sc_multi = len( names )
		return

	def allow_continuation( self, value = '\\' ):
		self.sc_do_backslash = value
		return

	def start( self ):
		# Called before first file is processed.
		return

	def process( self, name ):
		if name == '-':
			try:
				self.do_open_file( sys.stdin )
			except Exception as e:
				self.error( 'error handling {stdin}' )
				traceback.print_exc( file = sys.stderr )
				raise e
		elif os.path.isfile( name ):
			try:
				self._do_file( name )
			except Exception as e:
				self.error( 'processing "{0}"'.format( name ) )
				traceback.print_exc( file = sys.stderr )
				raise e
		elif os.path.isdir( name ):
			try:
				names = sorted( os.listdir( name ) )
			except Exception as e:
				self.error(
					'could not read directory "{0}"'.format( name ),
					e
				)
				traceback.print_exc( file = sys.stderr )
				raise ValueError
			self.sc_multi += len( names )
			for entry in names:
				if not self.ignore( entry ):
					try:
						self.process(
							os.path.join(
								name,
								entry
							)
						)
					except Exception as e:
						self.error(
							'could not process derived file "{0}"'.format(
								name
							),
							e
						)
		elif os.path.islink( name ):
			self.error( 'ignoring symlink "%s".' % name )
		else:
			self.error(
				'unknown file type, ignoring "%s".' % name,
				ValueError
			)
			traceback.print_exc( file = sys.stderr )
			raise ValueError
		return

	def pre_begin_file( self, fn = None ):
		return

	def begin_file( self, fn ):
		if self.sc_multi > 1:
			if self.sc_fileno > 1:
				self.println()
			self.println(
				'File %d of %d: %s' % (self.sc_fileno, self.sc_multi, fn)
			)
			self.println()
		return

	def end_file( self, fn ):
		if self.sc_fileno < self.sc_multi:
			self.println()
		self.sc_filename = None
		self.sc_lineno = 0
		return

	def post_end_file( self, name = None ):
		self.report()
		return

	def next_line( self, s ):
		self.println( s )
		return

	def _do_file( self, fn ):
		self.sc_fileno += 1
		self.sc_filename = fn
		self.sc_lineno = 0
		self.pre_begin_file( fn )
		self.begin_file( fn )
		if fn == '-':
			try:
				self.do_open_file( sys.stdin )
			except Exception as e:
				self.error( 'could not process "{stdin}"' )
				traceback.print_exc( file = sys.stderr )
				raise e
		else:
			try:
				with open( fn, 'rt' ) as f:
					try:
						self.do_open_file( f )
					except Exception as e:
						self.error( 'processing "{0}" failed.'.format( fn ) )
						traceback.print_exc( file = sys.stderr )
						raise e
			except Exception as e:
				self.error( 'could not open "{0}"'.format( fn ) )
				traceback.print_exc( file = sys.stderr )
				raise e
		self.end_file( fn )
		self.post_end_file()
		return

	def do_open_file( self, f = sys.stdin, name = '{stdin}' ):
		try:
			line = ''
			for segment in f:
				self.sc_lineno += 1
				line += segment.rstrip()
				if self.sc_do_backslash and len( line ) and line[-1] == self.sc_do_backslash:
					line[-1] = ' '
					continue
				self.next_line( line )
				line = ''
		except Exception as e:
			self.error( 'error processing file "{0}"'.format( name ) )
			raise e
		return

	def ignore( self, name ):
		return False

	def do_dir( self, dn ):
		for root,dirs,files in sorted( os.walk( dn ) ):
			self.sc_multi += len( files )
			for entry in files:
				if not self.ignore( entry ):
					self.do_file(
						os.path.join(
							root,
							entry
						)
					)
		if False:
			for dir in sorted( dirs ):
				self.do_dir(
					os.path.join(
						root,
						dir
					)
				)
		return

	def title( self, t = '', bar = '-' ):
		self.println( t )
		if bar:
			self.println( bar * len( t ) )
		self.println()
		return

	def println( self, s = '', out = None, end = '\n' ):
		if self.sc_linesout:
			say = '{0:7d} {1}'.format(
				self.get_linesout(),
				s
			)
		else:
			say = s
		print(
			say,
			file = out if out else self.sc_out,
			end  = end,
		)
		return

	def report( self, final = False ):
		# Called between file openings and at finish
		if not final:
			# Called at EOF of a file
			pass
		else:
			# Called after last file
			pass
		return

	def finish( self ):
		self.report( final = True )
		self.show_footnotes()
		return

	def error( self, msg, e = None ):
		self.sc_out.flush()
		clauses = list()
		if self.sc_filename is not None:
			clauses.append(
				'File %s' % self.sc_filename
			)
		if self.sc_lineno > 0:
			clauses.append(
				'Line %d' % self.sc_lineno,
			)
		prefix = ', '.join( clauses )
		print(
			'{0}: {1}'.format( prefix, msg ) if len( prefix ) else msg,
			file = sys.stderr
		)
		if e is not None:
			print(
				e,
				file = sys.stderr
			)
			traceback.print_exc( file = sys.stderr )
			raise e
		return

	def help( self, details = False ):
		self.println(
			self.HELPFMT % (
				self.NAME,
				self.DESCRIPTION
			)
		)
		if self.USAGE:
			self.println(
				self.HELPFMT % (
					'',
					self.USAGE
				)
			)
		if details:
			self.println(
				'',
				self.__doc__
			)
		return

	def next_footnote_pos( self ):
		return len(self.sc_footnotes) + 1

	def footnote( self, s ):
		N = self.next_footnote_pos()
		self.sc_footnotes.append( s )
		return N

	def title( self, text = '', bar = '-', spread = False ):
		if spread:
			text = ' '.join( [ c for c in text ] )
		self.println( text )
		if bar:
			self.println( bar * len( text ) )
		return

	def show_footnotes( self, title = 'Footnotes' ):
		if self.sc_footnotes:
			self.println()
			self.println( title )
			self.println( '-' * len( title ) )
			self.println()
			N = len( self.sc_footnotes )
			fmt = '{{0:{0}d}}. {{1}}'.format(
				len( str(N) )
			)
			for n,s in enumerate( self.sc_footnotes ):
				self.println(
					fmt.format( n+1, s )
				)
			self.sc_footnotes = None
		return
