#!/usr/bin/env python
# vim: et sw=4 ts=4

from    __future__      import  print_function

import  argparse
import  os
import  sys
import  traceback

try:
    import  importlib
except:
    class FunkyBob():
        def __init__( self ):
            pass
        def import_module( self, name ):
            try:
                module = __import__( name )
            except Exception as e:
                traceback.print_exc()
                raise ValueError(
                    'Could not import "{0}" using FunkyBob()'.format( name )
                )
            return module
    importlib = FunkyBob()

try:
    from  version   import  Version
except:
    Version = '0.0.0-bis'

class   chatter:
    def __init__( self, title, enabled = True ):
        self.title   = title
        self.enabled = enabled
        return
    def enable( self ):
        self.enabled = True
        return
    def disable( self ):
        self.enabled = False
        return
    def __enter__( self ):
        if self.enabled:
            print( '- entering {0}'.format( self.title ) )
        return
    def __exit__( self, type, value, tb ):
        if self.enabled:
            print( '- leaving {0}'.format( self.title ) )
        return

class   recursionlimit:

    def __init__( self, limit, title = None ):
        self.limit = limit
        self.title = title
        if self.title:
            print( '- entering {0}'.format( title ) )
        self.old_limit = sys.getrecursionlimit()

    def __enter__( self ):
        sys.setrecursionlimit( self.limit )
        if self.title:
            print( '- left {0}'.format( title ) )
        print
        return

    def __exit__( self, type, value, tb ):
        sys.setrecursionlimit( self.old_limit)
        return

class GenericPrettyPrinter( object ):

    NAME = 'N/A'
    USAGE = '%prog [-o file] [-t type] [file..]'
    DESCRIPTION = """Generic pretty-printer with loadable modules."""

    GLOB = '*'

    def __init__( self ):
        return

    def own_glob( self, pattern = None ):
        if not pattern:
            pattern = self.GLOB
        return glob.glob( pattern )

    def _session( self, Handler ):
        handler = Handler()
        if self.opts.number:
            handler.linesout_enable()
        # Allow plugin to figure out where its files are
        if len( self.opts.files ) == 0:
            self.opts.files = handler.own_glob()
        # Here is the session
        handler.start()
        handler.advise( self.opts.files )
        for name in self.opts.files:
            handler.process( name )
        handler.finish()
        return False

    def process( self, f = sys.stdin ):
        for line in f:
            self.println( line.rstrip() )
        return

    def main( self ):
        sys.path.insert( 0, os.path.dirname( __file__ ) )
        prog = os.path.splitext(
            os.path.basename( sys.argv[ 0 ] )
        )[ 0 ]
        if prog == '__init__':
            prog = 'genpp'
        # Intuit the kind of prettyprinter we want to be
        kind = 'text'
        if sys.argv[0].endswith( '-pp' ):
            kind = os.path.basename( sys.argv[0] )[:-3]
        p = argparse.ArgumentParser(
            description     = """A modular pretty printer that is easy to
            extend.""",
            prog            = prog,
#           usage           = '%{prog} [-o ofile] [-t type] [file..]',
#           version         = Version,
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            epilog = """Every attempt is made to provide a
            correctness-preserving tansformation.  The content may look
            different but correct input should result in correct output.
            The idea is for functionally-equivalent input to produce
            functionally-equivalent output so that two different file
            organizations can be compared, even if the line formatting
            differs or the line order differs."""
        )
        p.add_argument(
            '-D',
            '--debug',
            action  = 'count',
            dest    = 'debug_level',
            default =  0,
            help    = 'Increase debug verbosity.'
        )
        p.add_argument(
            '--version',
            action = 'version',
            version = Version,
            help = '{0} Version {1}'.format(
                prog,
                Version,
            )
        )
        p.add_argument(
            'files',
            metavar = 'FILE',
            nargs   = '*',
            help    = 'optional filenames',
#           action  = 'append',
#           type    = list,
#           default = [],
#           dest    = 'files',
#           default = [],
        )
        p.add_argument(
            '-N',
            '--number-lines',
            dest   = 'number_lines',
            help   = 'number output lines',
            action = 'store_const',
            const  = 0,
            default = None,
        )
        fake_ofile = '{stdout}'
        p.add_argument(
            '-o',
            '--out',
            dest    = 'ofile',
            action  = 'store',
            default =  fake_ofile,
            help    = 'output written to file',
            metavar = 'PATH'
        )
        p.add_argument(
            '-t',
            '--type',
            dest     = 'kind',
            action   = 'store',
            default  = kind,
            metavar  = 'TYPE',
            help     = 'kind of pretty-printer desired',
            required = (prog == 'genpp' ),
        )
        p.add_argument(
            '-n',
            '--number',
            dest   = 'number',
            action = 'store_true',
            help   = 'number output lines',
        )
        self.opts = p.parse_args()
        if self.opts.ofile == fake_ofile:
            self.opts.ofile = None
        # Here we go...
        module_name = '{0}-plugin'.format( self.opts.kind )
        try:
            if self.opts.debug_level > 0:
                print(
                    'Loading module {0}'.format(
                        module_name
                    ),
                    file = sys.stderr
                )
            with chatter( 'import_module', False ):
                module = importlib.import_module( module_name )
        except Exception as e:
            print(
                'No prettyprinter for "{0}".'.format( self.opts.kind ),
                file = sys.stderr
            )
            print(
                e,
                file = sys.stderr
            )
            traceback.print_exc( file = sys.stdout )
            return True
        if self.opts.ofile:
            try:
                sys.stdout = open( self.opts.ofile, 'wt' )
            except Exception as e:
                print(
                    'Cannot open "%s" for writing.'.format( self.opts.ofile ),
                    file = sys.stderr,
                )
                return True
        retval = self._session( module.PrettyPrint )
        return retval

if __name__ == '__main__':
    import  __main__
    genpp = GenericPrettyPrinter()
    retval = genpp.main()
    if retval:
        exit(1)
    exit(0)
