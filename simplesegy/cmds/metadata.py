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

import os
import Cheetah.Template 
from . import segy  # Added in python 2.5

def main():
    '''
    command line interface for templating 
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    parser.add_option('-t', '--template', dest='template', default=None,
                      help='Cheetah template to fill in')

    parser.add_option('-v', '--verbose', dest='verbose', default=False, action='store_true',
                      help='run the tests run in verbose mode')

    (options, args) = parser.parse_args()
    v = options.verbose

    for filename in args:
        filesize = os.path.getsize(filename) / 1000000. # Make it MB

        #sgy = simplesegy.segy.Segy(filename)
        sgy = segy.Segy(filename)
        (x_min,y_min),(x_max,y_max),(t_min,t_max) = sgy.trace_metadata()

        line_info = {
            'datetime_min':t_min,
            'datetime_max':t_max,
            'x_min':x_min,
            'x_max':x_max,
            'y_min':y_min,
            'y_max':y_max,
            }

        outfile = filename+'.metadata.txt'
        if v:
            print '''
            file: {infile} -> {outfile}
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


#if __name__ == '__main__':
#    main()
