#!/usr/bin/env python
# vim: noet sw=4 ts=4

import	sys
import	re
import	os

class	NatSort( object ):

	def	__init__( self ):
		super(NatSort,self).__init__()
		self.re = re.compile( r'([^0-9]+)|([0-9]+)' )
		return

	def	key( self, s ):
		chunks = [
			int(x) if x.isdigit() else x for x in self.re.split( s ) if x and len(x)
		]
		return chunks

	def	sorted( self, l ):
		keys = map(
			lambda s : self.key( s ),
			l
		)
		for l in sorted( keys ):
			yield ''.join([
				str(x) if isinstance( x, int ) else x for x in l
			])
		return

	def	main( self ):
		things = list()
		if len( sys.argv ) == 1:
			# stdin
			import	readline
			prompt = '{0}> '.format( sys.argv[0]) if os.isatty( sys.stdin.fileno() ) else None
			while True:
				try:
					s = raw_input( prompt )
				except EOFError:
					break
				things.append( s.rstrip() )
		else:
			for arg in sys.argv[1:]:
				with open( arg ) as f:
					things += map(
						str.rstrip,
						f.readlines()
					)
		for item in self.sorted( things ):
			print item
		return 0

if __name__ == '__main__':
	exit( NatSort().main() )
