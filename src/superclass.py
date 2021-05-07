#!/usr/bin/env python
# vim: et sw=4 ts=4

import  os
import  sys
import  glob
from    bunch   import  Bunch

class   MetaPrettyPrinter( object ):

    """
        Populate this!
    """

    NAME        = 'superclass'
    DESCRIPTION = 'Man behind the curtain.'
    USAGE       = None
    GLOB        = '*'
    HELPFMT     = '%23s | %s'

    def __init__( self ):
        self.reset()
        return

    def reset( self ):
        self.state = Bunch(
            out          = sys.stdout,
            fileno       = 0,
            lineno       = 0,
            filename     = '{stdin}',
            multi        = 0,
            do_backslash = None,
            footnotes    = [],
        )
        return  self.state

    def get_lineno( self ):
        return self.state.lineno

    def get_out( self ):
        return self.state.out

    def get_fileno( self ):
        return self.state.fileno

    def get_filename( self ):
        return self.state.filename

    def get_multi( self ):
        return self.multi

    def get_backslash( self ):
        return self.state.do_backlash

    def own_glob( self ):
        try:
            pattern = self.GLOB
            if pattern == '-':
                retval = '-'
            else:
                retval = glob.glob( pattern )
        except Exception as e:
            retval = [ '-' ]
        return retval

    def advise( self, names = [ '-' ] ):
        self.state.multi = len( names )
        return

    def allow_continuation( self, value = '\\' ):
        self.state.do_backslash = value
        return

    def start( self ):
        # Called before first file is processed.
        return

    def process( self, name ):
        if name == '-':
            try:
                self.do_open_file( sys.stdin )
            except Exception as e:
                self.error( 'error handling {stdin}' )
                raise e
        elif os.path.isfile( name ):
            try:
                self._do_file( name )
            except Exception as e:
                self.error( 'processing "{0}"'.format( name ) )
                raise e
        elif os.path.isdir( name ):
            try:
                names = sorted( os.listdir( name ) )
            except Exception as e:
                self.error(
                    'could not read directory "{0}"'.format( name ),
                    e
                )
                raise ValueError
            self.state.multi += len( names )
            for entry in names:
                if not self.ignore( entry ):
                    try:
                        self.process(
                            os.path.join(
                                name,
                                entry
                            )
                        )
                    except Exception as e:
                        self.error(
                            'could not process derived file "{0}"'.format(
                                name
                            ),
                            e
                        )
        elif os.path.islink( name ):
            self.error( 'ignoring symlink "%s".' % name )
        else:
            self.error(
                'unknown file type, ignoring "%s".' % name,
                ValueError
            )
            raise ValueError
        return

    def pre_begin_file( self, fn = None ):
        return

    def begin_file( self, fn ):
        if self.state.multi > 1:
            if self.state.fileno > 1:
                self.println()
            self.println(
                'File %d of %d: %s' % (self.state.fileno, self.state.multi, fn)
            )
            self.println()
        return

    def end_file( self, fn ):
        if self.state.fileno < self.state.multi:
            self.println()
        self.state.filename = None
        self.state.lineno = 0
        return

    def post_end_file( self, name = None ):
        self.report()
        return

    def next_line( self, s ):
        self.println( s )
        return

    def _do_file( self, fn ):
        self.state.fileno += 1
        self.state.filename = fn
        self.state.lineno = 0
        self.pre_begin_file( fn )
        self.begin_file( fn )
        if fn == '-':
            try:
                self.do_open_file( sys.stdin )
            except Exception as e:
                self.error( 'could not process "{stdin}"' )
                raise e
        else:
            try:
                with open( fn, 'rt' ) as f:
                    try:
                        self.do_open_file( f )
                    except Exception as e:
                        self.error( 'processing "{0}" failed.'.format( fn ) )
                        raise e
            except Exception as e:
                self.error( 'could not open "{0}"'.format( fn ) )
                raise e
        self.end_file( fn )
        self.post_end_file()
        return

    def do_open_file( self, f = sys.stdin, name = '{stdin}' ):
        try:
            line = ''
            for segment in f:
                self.state.lineno += 1
                line += segment.rstrip()
                if self.state.do_backslash and len( line ) and line[-1] == self.state.do_backslash:
                    line[-1] = ' '
                    continue
                self.next_line( line )
                line = ''
        except Exception as e:
            self.error( 'error processing file "{0}"'.format( name ) )
            raise e
        return

    def ignore( self, name ):
        return False

    def do_dir( self, dn ):
        for root,dirs,files in sorted( os.walk( dn ) ):
            self.state.multi += len( files )
            for entry in files:
                if not self.ignore( entry ):
                    self.do_file(
                        os.path.join(
                            root,
                            entry
                        )
                    )
        if False:
            for dir in sorted( dirs ):
                self.do_dir(
                    os.path.join(
                        root,
                        dir
                    )
                )
        return

    def title( self, t = '', bar = '-' ):
        self.println( t )
        if bar:
            self.println( bar * len( t ) )
        self.println()
        return

    def println( self, s = '', out = None, end = '\n' ):
        if self.cli.number_lines:
            self.cli.number_lines += 1
            leadin = f'{self.cli.number_lines:6d} '
        else:
            leadin = ''
        print(
            f'{leadin}{s}',
            file = out if out else self.state.out,
            end  = end,
        )
        return

    def report( self, final = False ):
        # Called between file openings and at finish
        return

    def finish( self ):
        self.report( final = True )
        self.show_footnotes()
        return

    def error( self, msg, e = None ):
        self.state.out.flush()
        clauses = list()
        if self.state.filename is not None:
            clauses.append(
                'File %s' % self.state.filename
            )
        if self.state.lineno > 0:
            clauses.append(
                'Line %d' % self.state.lineno,
            )
        prefix = ', '.join( clauses )
        print(
            '{0}: {1}'.format( prefix, msg ) if len( prefix ) else msg,
            file = sys.stderr
        )
        if e is not None:
            print(
                e,
                file = sys.stderr
            )
            raise e
        return

    def help( self, details = False ):
        self.println(
            self.HELPFMT % (
                self.NAME,
                self.DESCRIPTION
            )
        )
        if self.USAGE:
            self.println(
                self.HELPFMT % (
                    '',
                    self.USAGE
                )
            )
        if details:
            self.println(
                '',
                self.__doc__
            )
        return

    def next_footnote_pos( self ):
        return len(self.state.footnotes) + 1

    def footnote( self, s ):
        N = self.next_footnote_pos()
        self.state.footnotes.append( s )
        return N

    def title( self, text = '', bar = '-', spread = False ):
        if spread:
            text = ' '.join( [ c for c in text ] )
        self.println( text )
        if bar:
            self.println( bar * len( text ) )
        return

    def show_footnotes( self, title = 'Footnotes' ):
        if self.state.footnotes:
            self.println()
            self.println( title )
            self.println( '-' * len( title ) )
            self.println()
            N = len( self.state.footnotes )
            fmt = '{{0:{0}d}}. {{1}}'.format(
                len( str(N) )
            )
            for n,s in enumerate( self.state.footnotes ):
                self.println(
                    fmt.format( n+1, s )
                )
            self.state.footnotes = None
        return
