#!/usr/bin/python

import  pprint
import  sys
import  superclass
import  shlex
import  re

class   PrettyPrint( superclass.MetaPrettyPrinter ):

    NAME = 'udev'
    DESCRIPTION = """Display /etc/udev/rules.d/ files in canonical style."""

    GLOB = '*.rules'

    def __init__( self ):
        super( PrettyPrint, self ).__init__()
        self.lines = list()
        self.re = re.compile(
            r'^([^<>=]*[<>=]+)(.*)$'
        )
        self.allow_continuation()
        return

    def enquote( self, clause ):
        mo = self.re.match( clause )
        if mo:
            action = mo.group( 1 )
            predicate = mo.group( 2 )
            if predicate[-1] == ',':
                predicate = '"{0}",'.format( predicate[:-1] )
            else:
                predicate = '"{0}"'.format( predicate )
            new_clause = '{0}{1}'.format(
                action,
                predicate,
            )
        else:
            new_clause = clause
        return new_clause

    def next_line( self, line ):
        if line.startswith( '#' ):
            self.println( line )
        tokens = map(
            self.enquote,
            shlex.split( line, comments = True, posix = True )
        )
        self.lines.append( tokens )
        return

    def report( self, final = False ):
        if not final:
            self.println()
            self.title( 'RULES', spread = True )
            self.println()
            for tokens in self.lines:
                self.println( ' '.join( tokens ) )
            self.lines = list()
        return
