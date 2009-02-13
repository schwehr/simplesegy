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
@requires: U{cheetah<http://www.cheetahtemplate.org/>} >= 2.0

@undocumented: __doc__
@since: 2009-Jan-26
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import traceback
import os,sys
import Cheetah.Template 
#from . import segy  # Added in python 2.5
#from simplesegy import segy

#from . import segy  # Added in python 2.5
import simplesegy.segy as segy

def main():
    '''
    command line interface for templating 
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-t', '--template', dest='template', default=None,
                      help='Cheetah template to fill in')

    parser.add_option('-T', '--trace-trailer-size', dest='trace_trailer_size', default=0,
                      type='int',
                      help='If vendors put in extra data after each trace (ODEC needs 320) [default: %default]')

    parser.add_option('-B', '--byte-swap', dest='swap_byte_order', default=False, action='store_true',
                      help='Use this for files that have their byte order wrong (e.g. ODEC)')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    parser.add_option('--year', dest='force_year', default=None, type='int',
                      help='Force time [default: %default]')

    parser.add_option('--julian-day', dest='force_julian_day', default=None, type='int',
                      help='Force time [default: %default]')



    (options, args) = parser.parse_args()
    o = options
    v = o.verbose

    if (   (o.force_year is not None and o.force_julian_day is     None) 
        or (o.force_year is     None and o.force_julian_day is not None)):
        sys.exit('Must specify both year and julian day')

    for filename in args:
        filesize = os.path.getsize(filename) / 1000000. # Make it MB

        outfile = os.path.basename(filename)+'.metadata.txt'

        if v:
            print 'file: {infile} -> {outfile}'.format(infile=filename,outfile=outfile)

        try:
            sgy = segy.Segy(filename, swap_byte_order=o.swap_byte_order, trace_trailer_size=o.trace_trailer_size)
            sgy.filename = os.path.basename(filename)  # Drop the results in the current directory
            filename = os.path.basename(filename)  # Drop the results in the current directory

            (x_min,y_min),(x_max,y_max),(t_min,t_max) = sgy.trace_metadata()

            line_info = {
                'datetime_min':t_min,
                'datetime_max':t_max,
                'x_min':x_min,
                'x_max':x_max,
                'y_min':y_min,
                'y_max':y_max,
                }

            if v:
                print '''
    datetime_min: {datetime_min}
    datetime_max: {datetime_max}
           x_min: {x_min}
           x_max: {x_max}
           y_min: {y_min}
           y_max: {y_max}'''.format(infile=filename,outfile=outfile,**line_info)

            template=open(options.template).read()
            t = Cheetah.Template.Template(template,
                                              searchList=[line_info,
                                                          {'filename':filename,
                                                           'filesize':filesize}
                                                          ]
                                              )
            open(outfile,'w').write(str(t)) # "Render" the template to a file
        except Exception, e:
            sys.stderr.write('    Exception:' + str(type(Exception))+'\n')
            sys.stderr.write('    Exception args:'+ str(e)+'\n')
            traceback.print_exc(file=sys.stderr)
            sys.stderr.write('BAD file: %s\n' % filename)
            o = file(outfile+'.bad','w')
            o.write('BAD file: %s\n' % filename)
