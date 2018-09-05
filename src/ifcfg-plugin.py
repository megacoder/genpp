#!/usr/bin/python

from  	bunch		import	Bunch
import  pptree
import  superclass
import  sys

class   PrettyPrint( superclass.MetaPrettyPrinter ):

    NAME = 'ifcfg-pp'
    DESCRIPTION='''Show ifcfg network files in canonical style.'''

    def __init__( self ):
        super( PrettyPrint, self ).__init__()
        self.nic  = None
        self.nics = Bunch()
        return

    def ignore( self, name ):
        ''' Ignore directory entries not ending with '.conf' '''
        return not name.endswith( '.conf' )

    def node( self, DEVICE ):
        return bunch.Bunch(
            DEVICE   = DEVICE,
            parent   = None,
            children = list(),
        )

    def pre_begin_file( self, fn ):
        self.nic = self.node( 'TBD' )
        return

    def next_line( self, line ):
        parts = map(
            str.strip,
            line.split( '#', 1 )[ 0 ].split( '=', 1 )
        )
        if len( parts ) == 2:
            name  = parts[ 0 ]
            value = parts[ 1 ]
            self.nic[name] = value
        return

    def end_file( self, fn ):
        id = self.nic.DEVICE
        self.nics[ id ]   = self.nic
        # Leave the 'self.nic' intact so we can display it later in
        # self.report()
        return

    def choose(
        self,
        candidates,
        name = None,
        value = None,
        same = True,
        filter = None,
    ):
        if not candidates:
            candidates = [
                k for k in self.nics.keys() if not self.nics[k].parent
            ]
        if filter:
            candidates = [
                c for c in candidates if filter( c )
            ]
        if name:
            if same:
                candidates = [
                    id for id in candidates if
                        self.nics[id].get( name, '_dunno' ) == value
                ]
            else:
                candidates = [
                    id for id in candidates if
                        self.nics[id].get( name, '_dunno' ) != value
                ]
        return candidates

    def add_siblings( self, leadin ):
        candidates = self.choose(
            None,
            filter = lambda nic : self.nics[nic].DEVICE.startswith( leadin )
        )
        for candidate in sorted( candidates ):
            self.add_child( parent, candidate )
        return 

    def vlans_for( self, parent ):
        leadin = '{0}.'.format( parent )
        self.add_siblings( parent, leadin )
        return

    def aliases_for( self, parent ):
        leadin = '{0}:'.format( parent )
        self.add_siblings( parent, leadin )
        return

    def show_current_nic( self, nic, depth = 0 ):
        # Output iface lines, sorted in order
        keys = [
            key for key in self.nic if key[0].isupper()
        ]
        width =  max(
            map(
                len,
                keys
            )
        )
        fmt = '{{0:>{0}}}={{1}}'.format( width )
        for key in sorted( keys ):
            value = self.nic[ key ]
            print fmt.format(
                key,
                value,
            )
        return

    def add_child( self, parent, child ):
        self.nics[ child  ].parent = parent
        self.nics[ parent ].children.append( child )
        return

    def build_bond( self, parent, bond ):
        self.add_child( parent, bond )
        # Bonds are made out of NICs
        candidates = self.choose( None, 'TYPE', 'Ethernet' )
        paths = self.choose( candidates, 'MASTER', bond )
        for path in sorted( paths ):
            self.add_child( bond, path )
        pass

    def build_bridge( self, parent, bridge ):
        self.add_child( parent, bridge )
        # Bridges can be built from bonds
        candidates = self.choose( None, 'TYPE', 'Bridge' )
        bonds = self.choose( candidates, 'BRIDGE', bridge )
        for bond in sorted( bonds ):
            self.build_bond( bridge, bond )
        # Bridges can be simple NIC's
        candidates = self.choose( None, 'TYPE', 'Ethernet' )
        ethernets = self.choose( candidates, 'MASTER', bond )
        for ethernet in sorted( ethernets ):
            self.add_child( bridge, ethernet )
        return

    def report( self, final = False ):
        if final:
            self.print_network()
        else:
            self.print_nic()
        return

    def print_nic( self, nic = None ):
        if not nic:
            nic = self.nic
        width = max(
            map(
                len,
                self.nic.keys()
            )
        )
        fmt = '{{0:>{0}}}={{1}}'.format( width )
        for key in sorted( self.nic.keys() ):
            self.println(
                fmt.format( key, self.nic[ key ] )
            )
        return

    def print_network( self ):
        self.println()
        title = 'S U M M A R Y'
        self.println( title )
        self.println( '=' * len( title ) )
        # Step 0: The network (tm)
        self.println()
        network = self.node( DEVICE = 'network', NAME = 'network' )
        # Step 1: construct bridged interfaces
        bridges = self.choose( None, 'TYPE', 'Bridge' )
        for bridge in sorted( bridges ):
            self.build_bridge( network, bridge )
        # Step 2: Bonded interfaces
        bonds = self.choose( None, 'TYPE', 'Bond' )
        for bond in sorted( bonds ):
            self.build_bond( network, bond )
        # Step 3: Plain Ethernets (Infiniband?)
        ethernets = self.choose( None, 'TYPE', 'Ethernet' )
        for ethernet in sorted( ethernet ):
            self.add_child( network, ethernet )
        # Step 4: Show any left-overs
        unclaimed = self.choose()
        for solo in sorted( unclaimed ):
            self.add_child( network, solo )
        # Show what we have made
        print_tree( 
            network,
            nameattr = 'DEVICE',
            indent = 8,
        )
        return
