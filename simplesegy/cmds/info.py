#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Fill in a metadata template

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Feb-03
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import os, sys
import simplesegy.segy as segy

# FIX: make this discoverable pluging
from simplesegy.displays import text

def main():
    '''
    command line interface for templating 
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')

    parser.add_option('-f', '--format', dest='format', default='text',
                      help='print the text header')

#    parser.add_option('--summary', dest='summary', default=False, action='store_true',
#                      help='Summary data including bounding box, bounding time, and traces')

    
    parser.add_option('-t', '--text-header', dest='text_header', default=False, action='store_true',
                      help='print the text header')

    parser.add_option('-b', '--bin-header', dest='bin_header', default=False, action='store_true',
                      help='print the text header')

    parser.add_option('-n','--trace-num',dest='trace_num',default=None,
                      type='int',
                      help='Get info about a trace number (starts from 0)')

    parser.add_option('-a', '--all-traces', dest='all_traces', default=False, action='store_true',
                      help='Dump all traces')

    parser.add_option('-F','--trace-fields',dest='trace_fields', default = [],
                      action='append',
                      help='What fields to list for an all traces heading.  Sugegest "pos" and "time" [default: %default]')

    parser.add_option('-T', '--trace-trailer-size', dest='trace_trailer_size', default=0, 
                      help='If vendors put in extra data after each trace (ODEC needs 320) [default: %default]')

    parser.add_option('-B', '--byte-swap', dest='swap_byte_order', default=False, action='store_true',
                      help='Use this for files that have their byte order wrong (e.g. ODEC)')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    o = options
    v = o.verbose

    for filename in args:
        filesize = os.path.getsize(filename) / 1000000. # Make it MB

        sgy = segy.Segy(filename, swap_byte_order=o.swap_byte_order, trace_trailer_size=o.trace_trailer_size)


        # FIX: turn this into something plugable
        if o.format=='text':
            out = sys.stdout
            text.convert(out, sgy, 
                         text_header=o.text_header,
                         bin_header=o.bin_header,
                         all_traces=o.all_traces,
                         trace_fields=o.trace_fields,
                         trace_num=o.trace_num,
                         verbose=v
                         )
            #if o.trace is not None:
            #    print 'TRACE:'
                          
