#!/usr/bin/python
# vim: noet sw=4 ts=4

import	sys
import	os
import	re

class	Align( object ):

	def	__init__( self, lj = False, titles = 0 ):
		self.align_column = dict()
		self.align_title  = dict()
		self.items		  = []
		self.nItems		  = 0
		self.numeric	  = dict()
		self.titles		  = titles
		self.want_lj	  = lj
		self.widths		  = dict()
		self.align_map = dict(
			a = self._auto,
			c = self._center,
			l = self._left,
			r = self._right
		)
		self.re			  = re.compile(
			# Signed/unsigned integer|floating|scientific
			r'(^[-+]?[0-9]{1,}([.][0-9]{1,})?([Ee][-+]?[0-9]{1,})?)$'
		)
		return

	def	set_alignment( self, how = 'a' ):
		i = 0
		for key in range( self.get_columns() ):
			self.align_column[ key ] = self.align_map.get(
				how[ key % len( how ) ],
				self._auto
			)
			i = (i + 1) % len( how )
		return

	def	set_title_alignment( self, how = 'a' ):
		i = 0
		for key in range( self.get_columns() ):
			self.align_title[ key ] = self.align_map.get(
				how[ i ],
				self._auto
			)
			i = (i + 1) % len( how )
		return

	def	show_alignment( self, out = sys.stdout ):
		print(
			'Column Alignment'
		)
		for key in sorted( self.align_column ):
			print(
				'{0}\t{1}'.format( key, self.align_column[key] )
			)
		return

	def	show_title_alignment( self, out = sys.stdout ):
		print( 'Title Alignment' )
		for key in sorted( self.align_title ):
			print(
				'{0}\t{1}'.format( key, self.align_title[key] ),
				out  = out
			)
		return

	def	get_columns( self ):
		return len( self.widths.keys() )

	def	add( self, l ):
		# FIXME print( f'add( {l} )' )
		L = len( l )
		# Save to list of items in string format and remember facts
		F = list(
			map(
				str,
				l
			)
		)
		self.items.append( F )
		self.nItems += 1
		# Save column width and is column numeric
		for i in range( L ):
			self.widths[ i ] = max(
				self.widths.get( i, 1),
				len( F[i] )
			)
			# FIXME print( f'widths={self.widths}' )
			self.numeric[ i ] = self.numeric.get( i, True ) and self.re.match( F[i] )
		return

	def	_left( self, key, value ):
		# FIXME print( f'left key={key}, width={self.widths[key]}' )
		width = self.widths.get( key, 1 )
		fmt   = '|{{0:<{0}}}|'.format( width )
		# FIXME print( f'left={fmt}' )
		return fmt.format( value )

	def	_right( self, key, value ):
		# FIXME print( f'right key={key}, width={self.widths[key]}' )
		width = self.widths.get( key, 1 )
		fmt   = '|{{0:>{0}}}|'.format( width )
		# FIXME print( f'right={fmt}' )
		return fmt.format( value )

	def	_center( self, key, value, pad = ' ' ):
		# FIXME print( f'center key={key}, width={self.widths[key]}' )
		width = self.widths.get( key, 1 )
		fmt   = '|{{0:>{0}}}|'.format( width )
		# FIXME print( f'center={fmt}' )
		extra = int( (width - len( value )) / 2 )
		return fmt.format( value + (pad * extra) )

	def	_auto( self, key, value ):
		if self.numeric.get( key, False ):
			return self._right( key, value )
		if self.want_lj:
			return self._left( key, value )
		return self._right( key, value )

	def	get_items( self, sort = False ):
		if False:
			print(
				'widths={0}'.format(
					list([
						self.widths[ i ] for i in range( len( self.widths ) )
					])
				)
			)
		# Let auto columns inherit the justification of their column data
		for key in self.align_title.keys():
			if self.align_title[key] == self._auto:
				self.align_title[key] = self.align_column.get(
					key,
					self._auto
				)
		# Titles are first
		for row,tokens in enumerate( self.items[:self.titles] ):
			columns = []
			for key,token in enumerate( tokens ):
				columns.append(
					self.align_title.get( key, self._auto )( key, token )
				)
			# FIXME print( 'columns={0}'.format( columns ) )
			yield row,columns
		# Show data details lines
		if sort == False:
			sort = lambda x : 0
		elif sort == True:
			sort = lambda x : x
		for row,tokens in enumerate(
			sorted( self.items[self.titles:], key = sort )
		):
			columns = []
			for key,token in enumerate( tokens ):
				columns.append(
					(self.align_column.get( key, self._auto ))( key, token )
				)
			# FIXME print( 'columns={0}'.format( columns ) )
			yield self.titles+row,columns
		return

if __name__ == '__main__':
	a = Align( lj = True, titles = 1 )
	a.add( [ 'First', 'Second', '3rd', 'Fourth' ] )
	a.add( [ 1.2,22,3.33, 'astro' ] )
	a.add( [ 1,22,333, 'aSTRo' ] )
	a.add( [ -44,5,6, 'rubble' ] )
	a.add( [ 321,'abc','def', 123 ] )
	print(
		'Plain:'
	)
	a.set_title_alignment( 'rlca' )
	a.set_alignment( 'cccc' )
	for i,items in a.get_items():
		print( 'Line {0}->{1}'.format( i+1, ' '.join( items ) ) )
	print( 'Sorted' )
	a.set_title_alignment( 'llll' )
	a.set_alignment( 'aaaa' )
	for i,items in a.get_items( sort = True):
		print( 'Line {0}->{1}'.format( i+1, ' '.join( items ) ) )
	print( 'Weird' )
	a.set_title_alignment( 'a' )
	a.set_alignment( 'a' )
	import random
	how = lambda x : random.random()
	for i,items in a.get_items( sort = how ):
		print( 'Line {0}->{1}'.format( i+1, ' '.join( items ) ) )
