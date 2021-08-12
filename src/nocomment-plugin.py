#!/usr/bin/env python2

import  os
import  re
import  sys
import  math
import  superclass

class   PrettyPrint( superclass.MetaPrettyPrinter ):

    NAME = 'nocomment-pp'
    DESCRIPTION="""Plain text."""

    def __init__( self ):
        self.flags = 0
        self.rules = dict()
        self.default_rules()
        return

    def default_rules( self ):
        self.add_rule( r'[#].*$', '' )
        return

    def set_flags( self, flags ):
        self.flags = flags
        return

    def get_flags( self ):
        return self.flags

    def add_rule( self, name, rule ):
        self.rules[ name ] = re.compile( rule, self.flags )
        return

    def _process( self, line ):
        output = line
        for name in self.rules:
            output = re.sub( self.rules[ name ], '', output )
        return output

    def next_line( self, line ):
        self.println( self._process( line ) )
        return

if __name__ == '__main__':
    pp = PrettyPrint()
    pp.println(
        pp._process( 'abc#def' )
    )
    exit( 0 )
