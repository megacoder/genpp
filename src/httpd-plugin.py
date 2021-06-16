#!/usr/bin/env python
# vim: noet sw=4 ts=4

import	bunch
import	debug
import	os
import	shlex
import	superclass
import	sys

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME        = 'apache-pp'
	DESCRIPTION = """Print apache-style configuration files."""

	PLAIN = [ 'info', 'deviceuri' ]

	def	__init__( self ):
		super(PrettyPrint, self).__init__()
		self.gutter = '  '
		self.nodes  = list()
		self.root, root = self.new_node(
			key      = '{root}',
			tokens   = [ '<root/>' ],
			parent   = None,
			attrs    = list(),
			children = list(),
			line     = '{root}',
		)
		self.focus = self.root
		return

	def	new_node(
		self,
		key      = None,
		tokens   = list(),
		parent   = None,
		attrs    = list(),
		children = list(),
		line     = '',
	):
		node = bunch.Bunch(
			key      = key,
			tokens   = tokens,
			parent   = parent,		# Node ID of parent
			line     = line,
			attrs    = attrs,
			children = children,	# Array of child NID's
			nid      = len( self.nodes ),
		)
		self.nodes.append( node )
		return node.nid, node

	def	is_end( self, word ):
		return word.startswith( '</' )

	def	is_begin( self, word ):
		return word.startswith( '<' ) and not self.is_end( word )

	def	next_line( self, line ):
		tokens = list( shlex.split( line, posix = True, comments = True ) )
		if len(tokens):
			word = tokens[ 0 ]
			if self.is_begin( word ):
				nid, child = self.new_node(
					key    = line.strip(),
					parent = self.focus,
					tokens = tokens,
				)
				self.nodes[ self.focus ].children.append( nid )
				self.focus             = nid
				self.nodes[ nid ].line = line
			elif self.is_end( word ):
				self.focus = self.nodes[ self.focus ].parent
			else:
				self.nodes[ self.focus ].attrs.append( tokens )
		return

	def	quote_item( self, item ):
		delim = ''
		for p in [ ' ', '*', '|', '(', ')' ]:
			if p in item:
				delim = '"'
				break
		return '{0}{1}{0}'.format( delim, item )

	def	attr_fmts( self, node ):
		# Calculate widest entry in each column
		colwid  = list()
		ncolwid = 0
		for words in node.attrs:
			nwords = len( words )
			colwid += [ 1 ] * ( nwords - ncolwid )
			for i in range( nwords ):
				colwid[ i ] = max( colwid[ i ], len( words[ i ] ) )
			ncolwid = len( colwid )
		# Build padded format for each column
		fmts = map(
			lambda i : '{{0:{0}}}'.format( colwid[ i ] ),
			range( ncolwid )
		)
		return list( fmts )

	def	aligned_attr( self, node, fmts ):
		nfmts = len( fmts )
		for k,words in enumerate( sorted( node.attrs ) ):
			nwords = len( words )
			assert( nwords <= nfmts )
			padded = map(
				lambda i : fmts[ i ].format( words[ i ] ),
				range( nwords )
			)
			yield ' '.join( padded )
		return

	def	indented_println( self, s, depth = 0 ):
		self.println(
			'{0}{1}'.format(
				self.gutter * depth,
				s
			)
		)
		return

	def	do_print_node( self, nid, depth = 0, ):
		node = self.nodes[ nid ]
		if False:
			self.dump_node( node, 'About To Print' )
		# First line of node
		if depth > -1:
			self.indented_println(
				' '.join( node.tokens ),
				depth
			)
			section = node.key.split()[0].replace(
				'<', ''
			).replace(
				'>', ''
			)
		# Node attributes
		fmts = self.attr_fmts( node )
		for detail in self.aligned_attr( node, fmts ):
			self.indented_println(
				detail,
				depth + 1,
			)
		# Children
		for chid in sorted(
			node.children,
			key = lambda n : self.nodes[ n ].key
		):
			self.do_print_node(
				chid,
				depth + 1
			)
		# end the node
		if depth > -1:
			self.indented_println(
				'</{0}>'.format( section ),
				depth
			)
		return

	def	report( self, final = False ):
		if final:
			self.do_print_node(
				self.root,
				depth = -1
			)
		else:
			pass
		return

if __name__ == '__main__':
	pp = PrettyPrint()
	for line in sys.stdin:
		pp.next_line( line.rstrip() )
	pp.report( final = True )
	exit( 0 )
