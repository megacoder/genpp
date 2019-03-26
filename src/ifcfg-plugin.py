#!/usr/bin/python
# vim: ai sm noet ts=4 sw=4

import	bunch
import	natsort
from	pptree		import	Node, print_tree
import	natsort
import	superclass
import	sys
import	traceback

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'ifcfg-pp'
	DESCRIPTION = '''Show ifcfg network files in canonical style.'''
	UNSPECIFIED = '???'

	def __init__( self ):
		super( PrettyPrint, self ).__init__()
		self.ifcfg  = None
		self.ifcfgs = dict()
		return

	def ignore( self, name ):
		'''\
			Ignore anything but ifcfg-* files.
		'''
		return not name.startswith( 'ifcfg-' )

	def new_ifcfg( self, DEVICE ):
		'''\
			Takes a DEVICE name, returns a bunch.Bunch()
			node to be populated later.
		'''
		return bunch.Bunch(
			DEVICE = DEVICE,
			TYPE   = PrettyPrint.UNSPECIFIED,
			_used  = False,
		)

	def pre_begin_file( self, fn = None ):
		'''\
			Before beginning to process a new file,
			allocate a fresh bunch.Bunch() node to
			hold its attributes.
		'''
		try:
			self.ifcfg = self.new_ifcfg( 'TBD' )
		except Exception, e:
			traceback.print_exc()
			raise e
		return

	def	begin_file( self, fn ):
		'''\
			Called immediately before opening the
			named file.  Take advantage of this to
			write a section header before dumping
			the first NIC definition.
		'''
		if self.get_fileno() == 1:
			self.title( 'NIC CONFIGURATION' )
			self.println()
		super( PrettyPrint, self ).begin_file( fn )
		return

	def next_line( self, line ):
		'''\
			Called for each line of the current intput file.
			Whitespace at the right end of the line has been
			removed.  Continuation lines already processed.
		'''
		try:
			parts = map(
				str.strip,
				line.split( '#', 1 )[ 0 ].split( '=', 1 )
			)
			if len( parts ) == 2:
				name  = parts[ 0 ]
				value = parts[ 1 ]
				if len(value) and value[0] in [ '"', "'"] and value[0] == value[-1]:
					value = value[1:-1]
				self.ifcfg[ name ] = value
		except Exception, e:
			traceback.print_exc()
			raise e
		return

	def post_end_file( self, fn = None ):
		'''\
			Called after all lines from current file
			have been processed by next_line().  Add
			the new NIC definition to the catalog of
			NICs.  We'll print it from report() in
			a jiffy.'
		'''
		try:
			self.ifcfgs[ self.ifcfg.DEVICE ] = self.ifcfg
		except Exception, e:
			traceback.print_exc()
			raise e
		self.report()
		return

	def	set_used( self, name, value = True ):
		'''\
			Given a NIC device name, set
			(or clear) the usage flag.
		'''
		if name not in self.ifcfgs:
			self.println( 'name: {0}'.format( name ) )
			for n in sorted( self.ifcfgs ):
				self.println( '-- {0}'.format( n ) )
			raise ValueError(
				'set_used: name {0} not in known nics'.format( name )
			)
		self.ifcfgs[ name ]._used = value
		return

	def choose(
		self,
		candidates,			# List of names, required but 'None' is OK
		attr  = None,		# Filter on this, if present
		value = None,		# Value that 'attr' must have
		same  = True,		# Match if true, non-match if false
		used  = False,		# Entry must/must-not be used
		func  = None,		# Filter func( name )
	):
		'''\
			Collect a set of NIC device names
			where the NIC device meets a number
			of restraints.  If a list of names
			is not given, all known NICs are
			considered.  If an attribute name is
			given, its value must match the supplied
			value to remain a candidate.  We can also
			consider only used or unused NICs.
		'''
		if not candidates:
			candidates = self.ifcfgs.keys()
		if False:
			s = 'candidates={0}'.format( candidates )
			s += '; name="{0}"'.format( name )
			s += '; value="{0}"'.format( value )
			s += '; same={0}'.format( same )
			s += '; used={0}'.format( used )
			self.println( 'constraints={0}'.format( s ) )
		if isinstance( used, bool ):
			candidates = [
				name for name in candidates if self.ifcfgs[name]._used == used
			]
		if isinstance( attr, str ):
			if same:
				candidates = [
					name for name in candidates if
						self.ifcfgs[name][attr] == value
				]
			else:
				candidates = [
					name for name in candidates if
						self.ifcfgs[name][attr] != value
				]
		if func:
			candidates = [
				n for n in candidates if func( n ) == True
			]
		return sorted( candidates )

	def	assert_is_node( self, x ):
		assert(
			x is None or isinstance( x, Node )
		)
		return

	def node( self, name, pnode = None, claim = True ):
		self.assert_is_node( pnode )
		if claim and name in self.ifcfgs:
			self.set_used( name )
		self.assert_is_node( pnode )
		return Node(
			name,
			pnode,
		)

	def add_cousins( self, parent, leadin, flavor ):
		self.assert_is_node( parent )
		candidates = self.choose(
			None,
			func = lambda name : self.ifcfgs[ name ].DEVICE.startswith( leadin )
		)
		if len( candidates ):
			root = self.node( '<{0}>'.format( flavor ), parent )
		for candidate in candidates:
			_ = self.node( candidate, root )
		return

	def vlans_for( self, root ):
		self.assert_is_node( root )
		leadin = '{0}.'.format( root.name )
		self.add_cousins( root, leadin, 'vlan' )
		return

	def aliases_for( self, root ):
		self.assert_is_node( root )
		leadin = '{0}:'.format( root.name )
		self.add_cousins( root, leadin, 'alias' )
		return

	def show_ifcfg( self, ifcfg = None ):
		if not ifcfg:
			ifcfg = self.ifcfg
		attrs = [
			a for a in ifcfg if a.isupper()
		]
		width = max(
			map(
				len,
				attrs
			)
		)
		fmt = '{{0:>{0}}}={{1}}{{2}}{{1}}'.format( width )
		for attr in sorted( attrs ):
			value = ifcfg[ attr ]
			if value.isdigit():
				delim = ''
			elif ' ' in value or '\t' in value:
				delim = "'" if '"' in value else '"'
			else:
				delim = ''
			self.println(
				fmt.format( attr, delim, value )
			)
		return

	def	show_inventory( self ):
		'''\
			List all the ifcfg definitions we have, before
			we start making any changes to what we have been given.
		'''
		for i,name in enumerate( sorted( self.ifcfgs ) ):
			ifcfg = self.ifcfgs[ name ]
			attrs = ';'.join([
				'{0}={1}'.format(
					k, ifcfg[k]
				) for k in sorted( ifcfg )
			])
			self.println()
			self.println(
				'{0:2d} {1:<9} {2}'.format( i+1, name, attrs )
			)
		return

	def	build_ethernet( self, name, parent ):
		assert( isinstance( name, str ) )
		self.assert_is_node( parent )
		root = self.node( name, parent )
		branches = []
		return root, branches

	def	build_bond( self, name, parent ):
		root = self.node( name, parent )
		self.vlans_for( root )
		self.aliases_for( root )
		# Attach any Ethernet slaves
		children = self.choose(
			None,
			attr = 'MASTER',
			value = name
		)
		branches = []
		for moniker in children:
			node = self.node( moniker, root )
			branches.append( node )
		return root, branches

	def	build_bridge( self, name, parent ):
		root = self.node( name, parent )
		branches = []
		# Attach any Alias, Bond, Ethernet, or VLAN
		children = self.choose(
			None,
			attr  = 'BRIDGE',
			value = name
		)
		for moniker in children:
			node = self.node( moniker, root )
			branches.append( node )
			ifcfg = self.ifcfgs[ moniker ]
			if ifcfg.TYPE == 'Bond':
				_, _ = self.build_bond( moniker, node )
		return root, branches

	def	build_loopbacks( self, parent, candidates = None ):
		root = None
		branches = None
		if not candidates:
			candidates = self.choose(
				None,
				attr = 'DEVICE',
				value = 'lo',
			)
		if len( candidates ):
			root = self.node( '<loopback>', parent )
			branches = map(
				lambda name : self.node( name, root ),
				candidates
			)
		return root, branches

	def	build_orphans( self, parent ):
		self.assert_is_node( parent )
		orphans = self.choose( None, used = False )
		root = None
		branches = None
		if len( orphans ):
			root = self.node( '<orphans>', parent )
			branches = map(
				lambda name : self.node( name, root ),
				orphans
			)
		return root, branches

	def	resolve_unspecified( self ):
		# BONDING_OPTS implies NIC is a bond
		bond_type = 'Bond'
		for name in self.ifcfgs:
			if 'BONDING_OPTS' in dir( self.ifcfgs[name] ):
				if self.ifcfgs[ name ].TYPE != bond_type:
					self.println(
						'# {0}: retype {1}-->{2}'.format(
							name,
							self.ifcfgs[ name ].TYPE,
							bond_type
						)
					)
					self.ifcfgs[name].TYPE = bond_type
			if self.ifcfgs[name].SLAVE == 'YES':
				master = self.ifcfgs[name].MASTER
				if self.ifcfgs[ master ].TYPE != bond_type:
					self.println(
						'# {0}.{1}: forcing master type {2}-->{3}'.format(
							master,
							name,
							self.ifcfgs[ master ].TYPE,
							bond_type
						)
					)
				self.ifcfgs[ master ].TYPE = bond_type
			if name.startswith( 'eth' ):
				self.ifcfgs[ name ].TYPE = 'Ethernet'
		return

	def print_network( self ):
		self.title( 'S U M M A R Y', bar = '=' )
		self.title( 'Raw Inventory')
		if False:
			self.show_inventory()
		# Step 0: The network (tm); it's own parent, not it's own child
		# network = Node( 'network' )
		self.resolve_unspecified()
		network = self.node( '<network>', None )
		#
		root, branches = self.build_loopbacks( network )
		# BRIDGES
		candidates = self.choose( None, attr = 'TYPE', value = 'Bridge' )
		if len( candidates ):
			root = self.node( '<bridges>', network )
			for candidate in candidates:
				_, _ = self.build_bridge( candidate, root )
		# BONDS
		candidates = self.choose( None, attr = 'TYPE', value = 'Bond' )
		if len( candidates ):
			root = self.node( '<bonds>', network )
			for candidate in candidates:
				_, _ = self.build_bond( candidate, root )
		#
		candidates = self.choose( None, attr = 'TYPE', value = 'Ethernet' )
		if len( candidates ):
			root = self.node( '<ethernets>', network )
			for candidate in candidates:
				_, _ = self.build_ethernet( candidate, root )
		#
		#
		_, _ = self.build_orphans( network )
		#
		self.title( 'NETWORK DIAGRAM' )
		self.println()
		print_tree(
			network,
		)
		return

	def report( self, final = False ):
		if final:
			self.print_network()
		else:
			self.show_ifcfg()
		return
