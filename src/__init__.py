#!/usr/bin/env python2
# vim: et sw=4 ts=4

import  argparse
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
                    'Could not import "{0}"'.format( name )
                )
            return module
    importlib = FunkyBob()

import  os
import  sys

try:
    from  version   import  Version
except:
    Version = '0.0.0-bis'

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
        # Allow plugin to figure out where its files are
        if len( self.cli.files ) == 0:
            self.cli.files = handler.own_glob()
        # Here is the session
        handler.start()
        handler.cli = self.cli
        handler.advise( handler.cli.files )
        for name in handler.cli.files:
            handler.process( name )
        handler.finish()
        return False

    def process( self, f = sys.stdin ):
        for line in f:
            self.println( line.rstrip() )
        return

    def main( self ):
        # print( 'Generic prettyprinter (gpp) Version {0}'.format( Version ) )
        sys.path.insert( 0, os.path.dirname( __file__ ) )
        # Who are we?
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
            action  = 'store',
            type    = str,
            dest    = 'ofile',
            default =  fake_ofile,
            help    = 'output written to file',
            metavar = 'PATH'
        )
        p.add_argument(
            '-t',
            '--type',
            metavar  = 'TYPE',
            action   = 'store',
            type     = str,
            default  = 'text',
            dest     = 'kind',
            help     = 'kind of pretty-printer desired',
            required = True,
        )
        self.cli = p.parse_args()
        if self.cli.ofile == fake_ofile:
            self.cli.ofile = None
        # Here we go...
        module_name = '{0}-plugin'.format( self.cli.kind )
        try:
            if self.cli.debug_level > 0:
                self.println(
                    'Loading module {0}'.format(
                        module_name
                    ),
                    out = sys.stderr
                )
            module = importlib.import_module( module_name )
        except Exception as e:
            self.println(
                'No prettyprinter for "%s".'.format( self.cli.kind ),
                out = sys.stderr
            )
            self.println(
                e,
                out = sys.stderr
            )
            return True
        if self.cli.ofile:
            try:
                sys.stdout = open( self.cli.ofile, 'wt' )
            except Exception as e:
                self.println(
                    'Cannot open "%s" for writing.'.format( self.cli.ofile ),
                    out = sys.stderr,
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
