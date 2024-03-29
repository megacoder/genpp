#!/usr/bin/env python2

import	os
import	sys
import  superclass

class   PrettyPrint( superclass.MetaPrettyPrinter ):

    NAME = 'exports'
    DESCRIPTION = """Display /etc/exports files in canonical style."""

    def __init__( self ):
        super( PrettyPrint, self ).__init__()
        self.max_share = 7
        self.max_spec  = 15
        self.content   = []
        return

    def next_line( self, line ):
        tokens = line.split( '#', 1 )[0].strip().split()
        if len(tokens) > 0:
            # Format is
            #   <share> <host>(<param>[,...]) ...
            # Reformat only regular, or bind-mount, lines
            share = tokens[0]
            self.max_share = max( self.max_share, len(share) )
            roster = []
            for token in tokens[1:]:
                self.max_spec = max( self.max_spec, len(token) )
                lparen = token.find( '(' )
                if lparen > -1:
                    host = token[:lparen]
                    attrs = token[lparen+1:-1]
                    params = attrs.split( ',' )
                    params.sort()
                    ordered = ','.join( params )
                    roster.append( (host, ordered) )
            roster.sort( key = lambda hl: hl[0].lower() )
            self.content.append( (share, roster) )
        return

    def finish( self ):
        self.content.sort()
        share_fmt = '%%-%d.%ds'.format(self.max_share, self.max_share)
        spec_fmt  = ' %%-%d.%ds'.format(self.max_spec, self.max_spec)
        for share,roster in self.content:
            self.println(
                share_fmt.format( share )
            )
            for host,attrs in roster:
                howto = '%s(%s)' % (host,attrs)
                # Darn, this goes down, not across
                self.println( spec_fmt.format( howto ) )
            self.println()
        return
