#!/usr/bin/env python
"""Fill in a metadata template."""

import traceback
import os
import sys
import datetime
import time

import Cheetah.Template

import simplesegy.segy as segy
from simplesegy.cmds import common_opts

def main():
    '''
    command line interface for templating
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-t', '--template', dest='template', default=None,
                      help='Cheetah template to fill in')

    parser.add_option('--year', dest='force_year', default=None, type='int',
                      help='Force time [default: %default]')

    parser.add_option('--julian-day', dest='force_julian_day', default=None, type='int',
                      help='Force time [default: %default]')

    common_opts.add_odec(parser)

    common_opts.add_verbose(parser)

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

            if ( (t_min is None or t_max is None) and o.force_year is None):
                sys.exit('ERROR: bad time range.  Can you force it?')

            if o.force_year is not None:
                t_min = None
                t_max = None
                last_hour = None
                if v:
                    sys.stderr.write('Computing forced time range assuming hour, min, sec are valid')
                for tracecount,trace in enumerate(sgy):
                    if last_hour is not None and last_hour > trace.hour:
                        raise SegyError('File spans days.  That is not okay for forced year/julian day')
                    last_hour = trace.hour
                    t = time.strptime('%4d %03d' % (o.force_year,o.force_julian_day),'%Y %j')
                    t = datetime.datetime(o.force_year,t.tm_mon,t.tm_mday,trace.hour,trace.min,trace.sec)
                    if not t_min:
                        t_min = t
                    t_max = t

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
