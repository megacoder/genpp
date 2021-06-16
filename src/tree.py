#!/usr/bin/env python
# vim: noet sw=4 ts=4

from	__future__				import	print_function

import	sys
import	os
import	bunch

import	traceback

class	Tree( bunch.Bunch ):

	SPECIAL = [ 'name', 'parent', 'left', 'right', 'data' ]

	def	__init__(
		self,
		name   = None,
		left   = None,
		right  = None,
		data   = bunch.Bunch(),
		parent = None
	):
		self.name   = name
		self.parent = parent
		self.left   = left
		self.right  = right
		self.data   = data
		return

	def	__getattribute__( self, name ):
		if name not in Tree.SPECIAL:
			return self.attrs[ name ]
		return self.data[ name ]

	def	__setattr__( self, name, value ):
		if name not in Tree.SPECIAL:
			self.attrs[ name ] = value
		else:
			self.__setattr_( name, value )
		return

	def	__repr__( self ):
		return  '"{0}": p={1}, l={2}, r={3}, v={4}'.format(
			self.attrs.name,
			self.attrs.parent,
			self.attrs.left,
			self.attrs.right,
			self.attrs.data,
		)

if __name__ == '__main__':
	try:
		t       = Tree( 'ADAM' )
		t.left  = Tree( 'CHILD' )
		t.right = Tree( 'SIBLING' )
		print( t )
	except Exception as e:
		print( e )
		traceback.print_exc()
