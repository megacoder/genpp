#!/usr/bin/python
# vi: noet sw=4 ts=4

import	os
import	sys
import	superclass
import	string
from	bunch		import	Bunch

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'iptables-nvl-pp'
	DESCRIPTION = """Display 'iptables -nvL' output in canonical style."""

	def	__init__( self ):
		super( PrettyPrint, self ).__init__()
		self.chains  = dict()
		self.titles  = list()
		self.widths  = list()
		return

	def	pre_begin_file( self, name = None ):
		self._add_chain()
		return

	def	own_glob( self ):
		return '-'

	def	_add_chain( self ):
		if self.chain and self.chain.name:
			self.chains[ self.chain.name ] = self.chain
		self.chain        = Bunch()
		self.chain.name   = None
		self.chain.info   = list()
		self.chain.rules  = list()
		return

	def	next_line( self, line ):
		tokens = line.split()
		N = len( tokens )
		if N:
			key = tokens[0]
			if key == 'Chain':
				# New chain
				name = tokens[ 1 ]
				self._add_chain( name )
				self.chain.info = tokens
			elif key == 'pkts':
				# Column headers
				if not self.titles:
					self.titles = tokens
					self.widths = map(
						len,
						self.titles
					)
			else:
				# Everything else
				self.chain.rules.append( tokens )
				for i in range( N ):
					self.widths[ i ] = max(
						self.widths[ i ],
						len( tokens[ i ] )
					)
		return

	def	post_close_file( self, name = None ):
		self._add_chain()
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
				if k:
					# Separator
					self.println()
				self.println( ' '.join( self.info ) )
				# Column headers
				N = len( self.titles )
				self.println(
					' '.join(
						map(
							lambda i : fmts[i].format( self.titles[ i] ),
							range( N )
						)
					)
				)
				# Each rule on a separate line
				for rule in self.chain[ name ].rules:
					self.println(
						' '.join(
							lambda i : fmts[ i ].format( rule[ i ] ),
							range( N )
						)
					)
			)
		return
