#!/usr/bin/python
# vim: ai sm noet ts=4 sw=4

import	bunch
import	pptree
import	superclass
import	sys
import	traceback

class	PrettyPrint( superclass.MetaPrettyPrinter ):

	NAME = 'ifcfg-pp'
	DESCRIPTION = '''Show ifcfg network files in canonical style.'''
	UNSPECIFIED = '???'

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

	def add_nic( self, DEVICE ):
		'''\
			Takes a DEVICE name, returns a Bunch() node to
			be populated later.
		'''
		return bunch.Bunch(
			DEVICE = DEVICE,
			TYPE   = PrettyPrint.UNSPECIFIED,
			_used  = False,
		)

	def pre_begin_file( self, fn = None ):
		'''\
			Before beginning to process a new file,
			allocate a fresh Bunch() node to hold
			its attributes.
		'''
		try:
			self.nic = self.add_nic( 'TBD' )
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
				self.nic.TYPE = 'Dunno'
			self.nics[ self.nic.DEVICE ] = self.nic
			# Leave the 'self.nic' intact so we can display it later in
			# self.report()
		except Exception, e:
			traceback.print_exc()
			raise e
		return

	def	set_used( self, name, value = True ):
		'''\
			Given a NIC device name, set
			(or clear) the usage flag.
		'''
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
		candidates,			# List of names, required but 'None' is OK
		attr   = None,		# Filter on this, if present
		value  = None,		# Value that 'attr' must have
		same   = True,		# Match if true, non-match if false
		used   = False,		# Entry must/must-not be used
		claim  = True,		# Set usage flag if chosen
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
			candidates = self.nics.keys()
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
				name for name in candidates if self.nics[name]._used == used
			]
		if isinstance( attr, str ):
			if same:
				candidates = [
					name for name in candidates if
						self.nics[name][attr] == value
				]
			else:
				candidates = [
					name for name in candidates if
						self.nics[name][attr] != value
				]
		if isinstance( claim, bool ):
			map(
				lambda n : self.set_used( n, claim ),
				candidates
			)
		return sorted( candidates )

	def node( self, name, pnode = None ):
		if name in self.nics:
			self.set_used( name )
		return pptree.Node(
			name,
			pnode,
		)

	def add_siblings( self, sibling, leadin ):
		candidates = self.choose(
			None,
			claim = False
		)
		candidates = [
			k for k in candidates if self.nics[k].DEVICE.startswith( leadin )
		]
		map(
			lambda n : self.node( sibling, n ),
			candidates
		)
		return candidates

	def vlans_for( self, sibling, name ):
		leadin = '{0}.'.format( name )
		return	self.add_siblings( sibling, leadin )

	def aliases_for( self, sibling, name ):
		leadin = '{0}:'.format( name )
		return self.add_siblings( sibling, leadin )

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

	def	show_inventory( self ):
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

	def	build_ethernets( self, parent, candidates = None ):
		if not candidates:
			candidates = self.choose(
				None,
				'TYPE',
				'Ethernet',
			)
		if len( candidates ):
			ethers = self.node( '<ethers>', parent )
			map(
				lambda n : self.node( n, ethers ),
				candidates
			)
		return candidates

	def	build_bonds( self, parent, candidates = None ):
		if not candidates:
			candidates = self.choose(
				None,
				'TYPE',
				'Bond',
			)
		if len( candidates ):
			bonode = self.node( '<bonds>', parent )
			map(
				lambda n : self.node( n, bonode ),
				candidates
			)
		return candidates

	def	build_bridges( self, parent, candidates = None ):
		if not candidates:
			candidates = self.choose(
				None,
				'TYPE',
				'Bridge',
			)
		if len( candidates ):
			brnode = self.node( '<bridges>', parent )
			map(
				lambda n : self.node( n, brnode ),
				candidates
			)
		return candidates

	def	claim_loopback( self, parent, candidates = None ):
		if not candidates:
			candidates = self.choose(
				None,
				'DEVICE',
				'lo',
			)
		map(
			lambda n : self.node( n, parent ),
			candidates
		)
		return candidates

	def	resolve_unspecified( self ):
		# BONDING_OPTS implies NIC is a bond
		for n in self.nics:
			if 'BONDING_OPTS' in dir( self.nics[n] ):
				self.nics[n].TYPE = 'Bond'
		return

	def	build_orphans( self, parent ):
		orphans = self.choose( None, used = False )
		if len( orphans ):
			orphanage = self.node( '<orphans>', parent )
			map(
				lambda n : self.node( n, orphanage ),
				orphans
			)
		else:
			self.title( 'No orphans' )
		return parent

	def print_network( self ):
		self.title( 'S U M M A R Y', bar = '=' )
		self.title( 'Raw Inventory')
		self.show_inventory()
		# Step 0: The network (tm); it's own parent, not it's own child
		# network = pptree.Node( 'network' )
		self.resolve_unspecified()
		network = self.node( '<network>', None )
		self.claim_loopback( network )
		self.build_bridges( network )
		self.build_bonds( network )
		self.build_ethernets( network )
		self.build_orphans( network )
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
