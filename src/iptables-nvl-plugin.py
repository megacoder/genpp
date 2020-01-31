#!/usr/bin/env python2
# vi: noet sw=4 ts=4

import	os
import	sys
import	superclass
import	string
from	bunch		import	Bunch

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'iptables-nvL-pp'
	DESCRIPTION = """Display 'iptables -nvL' output in canonical style."""

	def	__init__( self ):
		super( PrettyPrint, self ).__init__()
		self.chains  = dict()
		self.titles  = None
		self.widths  = []
		return

	def	pre_begin_file( self, name = None ):
		self.chain = self._new_chain()
		return

	def	_new_chain( self, name = None, info = None, rules = list() ):
		return Bunch(
			name  = name,
			info  = info,
			rules = rules,
		)

	def	_end_chain( self ):
		if self.chain.name:
			self.chains[ self.chain.name ] = self.chain
		self.chain = self._new_chain()
		return

	def	check_widths( self, d ):
		nD          = len( d )
		nWidths     = len( self.widths )
		need        = nD - nWidths
		self.widths += [ 0 ] * need
		self.widths = map(
			lambda i: max(
				self.widths[ i ],
				len( d[ i ] )
			),
			range( nD )
		)
		return

	def	_end_chain( self, name = None ):
		if not name:
			name = self.chain.name
		self.chains[ name ] = self.chain


	def	next_line( self, line ):
		tokens = line.split()
		N = len( tokens )
		if N == 0:
			# Blank line ends ruleset
			self._end_chain()
		else:
			key = tokens[0]
			if key == 'Chain':
				# New chain
				name = tokens[ 1 ]
				self.chain = self._new_chain(
					name = name,
					info = tokens,
				)
			elif key == 'pkts':
				self.titles = tokens
				self.check_widths( tokens )
			else:
				# Everything else
				self.chain.rules.append( tokens )
				self.check_widths( tokens )
		return

	def	post_end_file( self, name = None ):
		self._end_chain()
		self.report()
		return

	def	report( self, final = False ):
		if not final:
			# Conjure up the column format strings
			fmts = map(
				'{{0:{0}}}'.format,
				self.widths
			)
			N = len( self.widths )
			# For every defined chain:
			for k,name in enumerate( sorted( self.chains ) ):
				if k == 0:
					self.println( '# Defined iptables(8) chains.')
				# Separator
				self.println()
				title = ' '.join( self.chains[ name ].info )
				self.println( '## {0}'.format( title ) )
				self.println()
				# Column headers
				self.println(
					' '.join(
						map(
							lambda i : fmts[i].format( self.titles[ i ] ),
							range( N )
						)
					)
				)
				# Each rule on a separate line
				for rule in self.chains[ name ].rules:
					self.println(
						' '.join(
							map(
								lambda i : fmts[ i ].format( rule[ i ] ),
								range( N )
							)
						)
					)
		return
