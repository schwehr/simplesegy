#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Slice a number of traces out of segy file

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{cheetah<http://www.cheetahtemplate.org/>} >= 2.0

@undocumented: __doc__
@since: 2009-Feb-12
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import traceback
import os,sys

import simplesegy.segy as segy


def slice(sgy,outfile, force_ascii=False, start_trace=0, end_trace=None, verbose=False):
        v = verbose
        out = file(outfile,'wb')

        # Text header
        if force_ascii:
            out.write(sgy.hdr_text)
        else:
            out.write(sgy.data[0:3200])

        # Binary header
        out.write(sgy.data[3200:3200+400])

        # Extended text headers
        if force_ascii:
            for text in sgy.extended_text_hdrs:
                out.write(text)
        else:
            if 0 < len(sgy.extended_text_hdrs):
                out.write(sgy.data[3201+400:sgy.trace_start])

        if 0 > start_trace or 0 > end_trace:
            sys.exit('ERROR: trace indices relative to the end not yet implemented')

        if end_trace is None:
            for i,trace in enumerate(sgy):
                if i < start_trace:
                    continue
                if i == end_trace:
                    break
                out.write(trace.get_trace_data)

        else:
            for i in range(start_trace, end_trace):
                if v and i%100==0:
                    print 'trace',i
                print 'FIX: looking up trace',i
                trace = sgy[i]

                out.write(trace.get_trace_data())


def main():
    '''
    command line interface for templating 
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-s', '--start-trace', dest='start_trace', default=0,
                      type = 'int',
                      help='Beginning trace.  Counting starts at 0.  Use negative numbers for relative to the end of file [default: %default]')

    parser.add_option('-e', '--end-trace', dest='end_trace', default=None,
                      type = 'int',
                      help='Ending  trace.  Counting starts at 0.  Use negative numbers for relative to the end of file [default: end of file]')

    parser.add_option('--force-ascii',dest='force_ascii', default=False,
                      action='store_true',
                      help='Make sure to convert the text header and extended text headers to ascii [default: %default]')

    parser.add_option('-T', '--trace-trailer-size', dest='trace_trailer_size', default=0,
                      type='int',
                      help='If vendors put in extra data after each trace (ODEC needs 320) [default: %default]')

    parser.add_option('-B', '--byte-swap', dest='swap_byte_order', default=False, action='store_true',
                      help='Use this for files that have their byte order wrong (e.g. ODEC)')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (opt, args) = parser.parse_args()
    
    v = opt.verbose

    for filename in args:

        outfile = os.path.basename(filename)+'.out'

        if v:
            print 'file: {infile} -> {outfile}'.format(infile=filename,outfile=outfile)

        sgy = segy.Segy(filename, swap_byte_order=opt.swap_byte_order, trace_trailer_size=opt.trace_trailer_size)

        slice(sgy, outfile, opt.force_ascii, opt.start_trace, opt.end_trace, verbose=v)

#         out = file(outfile,'wb')

#         # Text header
#         if opt.force_ascii:
#             out.write(sgy.hdr_text)
#         else:
#             out.write(sgy.data[0:3200])

#         # Binary header
#         out.write(sgy.data[3201:3201+400])

#         if opt.force_ascii:
#             for text in sgy.extended_text_hdrs:
#                 out.write(text)
#         else:
#             if 0<len(sgy.extended_txt_hdrs):
#                 out.write(sgy.data[3201+400:sgy.trace_start])

#         if 0 > opt.start_trace or 0 > opt.end_trace:
#             sys.exit('ERROR: trace indices relative to the end not yet implemented')

#         if opt.end_trace is None:
#             for i,trace in enumerate(sgy):
#                 if i<opt.start_trace:
#                     continue
#                 if i==opt.end_trace:
#                     break
#                 out.write(trace.get_trace_data)

#         #print opt.start_trace,opt.end_trace,'->',range(opt.start_trace,opt.end_trace)
#         else:
#             for i in range(opt.start_trace,opt.end_trace):
#                 if v and i%100==0:
#                     print 'trace',i
#                 trace = sgy[i]

#                 out.write(trace.get_trace_data())

