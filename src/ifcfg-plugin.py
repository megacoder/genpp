#!/usr/bin/python
# vim: ai sm noet ts=4 sw=4

import	bunch
import	pptree
import	superclass
import	sys
import	traceback

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'ifcfg-pp'
	DESCRIPTION='''Show ifcfg network files in canonical style.'''

	def __init__( self ):
		super( PrettyPrint, self ).__init__()
		self.nic  = None
		self.nics = dict()
		return

	def ignore( self, name ):
		'''\
			Ignore anything but ifcfg-* files.
		'''
		return not name.startswith( 'ifcfg-' )

	def node( self, DEVICE ):
		'''\
			Takes a DEVICE name, returns a Bunch() node to
			be populated later.
		'''
		return bunch.Bunch(
			DEVICE = DEVICE,
			_used  = False,
		)

	def pre_begin_file( self, fn = None ):
		'''\
			Before beginning to process a new file,
			allocate a fresh Bunch() node to hold
			its attributes.
		'''
		try:
			self.nic = self.node( 'TBD' )
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
				self.nic[ name ] = value
		except Exception, e:
			traceback.print_exc()
			raise e
		return

	def end_file( self, fn = None ):
		'''\
			Called after all lines from current file
			have been processed by next_line().  Add
			the new NIC definition to the catalog of
			NICs.  We'll print it from report() in
			a jiffy.'
		'''
		try:
			if 'TYPE' not in self.nic:
				self.nic.TYPE = 'Ethernet'
			self.nics[ self.nic.DEVICE ] = self.nic
			# Leave the 'self.nic' intact so we can display it later in
			# self.report()
		except Exception, e:
			traceback.print_exc()
			raise e
		return

	def	get_used( self, name ):
		'''\
			Given a NIC name, return True if
			the NIC has been claimed already,
			else return False.
		'''
		if True:
			if name not in self.nics:
				raise ValueError(
					'get_used: name {0} not in known nics'.format( name )
				)
		return self.nics[ name ]._used

	def	set_used( self, name, value = True ):
		'''\
			Given a NIC device name, set
			(or clear) the usage flag.
		'''
		if True:
			if name not in self.nics:
				self.println( 'name: {0}'.format( name ) )
				for nic in sorted( self.nics ):
					self.println( '-- {0}'.format( nic ) )
				raise ValueError(
					'set_used: name {0} not in known nics'.format( name )
				)
		self.nics[ name ]._used = value
		return

	def choose(
		self,
		candidates,			# List of strings
		name   = None,
		value  = None,
		same   = True,
		used   = False,
		claim  = None,
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
			Set "claim" to True to mark the NIC
			as having been consumed.
		'''
		if not candidates:
			candidates = [ k for k in self.nics ]
		if False:
			s = 'candidates={0}'.format( candidates )
			s += '; name="{0}"'.format( name )
			s += '; value="{0}"'.format( value )
			s += '; same={0}'.format( same )
			s += '; used={0}'.format( used )
			s += '; claim={0}'.format( claim )
			self.println( 'constraints={0}'.format( s ) )
		if isinstance( used, bool ):
			candidates = [
				k for k in candidates if self.get_used( k ) == used
			]
		if isinstance( name, str ):
			if same:
				candidates = [
					k for k in candidates if
						(self.nics[k][name] == value)
				]
			else:
				candidates = [
					k for k in candidates if
						(self.nics[k][name] != value)
				]
		if isinstance( claim, bool ):
			for c in candidates:
				self.set_used( c, claim )
		if False:
			self.println(
				'chosen={0}'.format( candidates )
			)
		return candidates

	def add_child( self, parent, name, kind = 'child' ):
		if False:
			self.println(
				'*** adding {0} {1} to {2}'.format(
				kind,
				name,
				parent.name
			)
		)
		if True:
			if not isinstance( parent, pptree.Node ):
				raise ValueError( 'Must be node, not ()({1}) {2})'.format(
					parent,
					name
				))
			if not isinstance( name, str ):
				raise ValueError(
					'child must be str(), not ()({0}){1})'.format(
						type( name ),
						name
					)
				)
		self.set_used( name )
		return pptree.Node( name, parent )

	def add_siblings( self, sibling, leadin ):
		candidates = self.choose(
			None,
		)
		candidates = [
			k for k in candidates if self.nics[k].DEVICE.startswith( leadin )
		]
		for candidate in sorted( candidates ):
			self.add_child( sibling, candidate )
		return

	def vlans_for( self, sibling, name ):
		leadin = '{0}.'.format( name )
		self.add_siblings( sibling, leadin )
		return

	def aliases_for( self, sibling, name ):
		leadin = '{0}:'.format( name )
		self.add_siblings( sibling, leadin )
		return

	def	build_ethernets( self, parent, ethernets ):
		if False:
			self.println(
				'*** adding Ethernets {0} to {1}'.format(
				ethernets,
				parent.name,
			)
		)
		for ethernet in sorted( ethernets ):
			self.add_child(   parent, ethernet, 'path' )
			self.vlans_for(   parent, ethernet )
			self.aliases_for( parent, ethernet )
		return

	def build_bonds( self, parent, bonds ):
		for bond in sorted( bonds ):
			bond_n = self.add_child( parent, bond )
			self.vlans_for( bond_n, bond )
			self.aliases_for( bond_n, bond )
			# Bonds are made out of NICs, our NICs
			ethernets = self.choose(
				None,
				'TYPE',
				'Ethernet',
			)
			ethernets = [
				k for k in ethernets if self.nics[k].MASTER == bond
			]
			self.build_ethernets( bond_n, ethernets )
		return

	def build_bridges( self, parent, names ):
		for name in sorted( names ):
			bridge_n = self.add_child( parent, name, 'bridge' )
			self.vlans_for( bridge_n, name )
			self.aliases_for( bridge_n, name )
			# Bridges can be built from bonds
			bonds = self.choose(
				None,
				'TYPE',
				'Bond',
			)
			bonds = [
				k for k in self.nics if self.nics[k].BRIDGE == name
			]
			self.build_bonds( bridge_n, bonds )
			# Bridges can be simple NICs, our NICs
			ethernets = self.choose(
				None,
				'TYPE',
				'Ethernet',
			)
			ethernets = [
				k for k in ethernets if self.nics[k].MASTER == name
			]
			self.build_ethernets( bridge_n, ethernets )
		return

	def	build_orphans( self, parent ):
		orphans = [
			k for k in self.nics if self.get_used( k ) == False
		]
		for orphan in sorted( orphans ):
			self.add_child(
				parent,
				orphan,
				'orphan'
			)
		return

	def print_nic( self, nic = None ):
		if not nic:
			nic = self.nic
		if nic:
			attrs = [
				a for a in self.nic if a.isupper()
			]
			width = max(
				map(
					len,
					attrs
				)
			)
			fmt = '{{0:>{0}}}={{1}}{{2}}{{1}}'.format( width )
			for attr in sorted( attrs ):
				value = self.nic[ attr ]
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

	def	title( self, s, id = '-' ):
		self.println()
		self.println( s )
		self.println( id * len( s ) )
		return

	def	show_inventory( self ):
		self.title( 'INVENTORY' )
		for i,name in enumerate( sorted( self.nics ) ):
			nic = self.nics[ name ]
			attrs = ';'.join([
				'{0}={1}'.format(
					k, nic[k]
				) for k in sorted( nic )
			])
			self.println()
			self.println(
				'{0:2d} {1:<9} {2}'.format( i+1, name, attrs )
			)
		return

	def print_network( self ):
		self.title( 'S U M M A R Y', '=' )
		if False:
			self.show_inventory()
		# Step 0: The network (tm); it's own parent, not it's own child
		network = pptree.Node( 'network' )
		if False:
			# Step 1: construct bridged interfaces
			bridges = self.choose( None, 'TYPE', 'Bridge' )
			self.build_bridges( network, bridges )
			# Step 2: Bonded interfaces
			bonds = self.choose( None, 'TYPE', 'Bond' )
			self.build_bonds( network, bonds )
		# Step 3: Plain Ethernets (Infiniband?)
		ethernets = self.choose( None, 'TYPE', 'Ethernet' )
		self.build_ethernets( network, ethernets )
		# Step 4: Claim any left-overs
		self.build_orphans( network )
		# Step 5: Show our network diagram
		self.title( 'NETWORK DIAGRAM' )
		self.println()
		pptree.print_tree(
			network,
		)
		return

	def report( self, final = False ):
		try:
			if final:
				self.print_network()
			else:
				self.print_nic()
		except Exception, e:
			traceback.print_exc()
			raise e
		return
