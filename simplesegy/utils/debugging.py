#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Deubugging utilities

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Feb-09
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''
import sys

def checkpoint(out=sys.stdout):
    '''Print where this function was called from in a standard format
    that looks like a compiler error'''

    import inspect
    f = inspect.currentframe().f_back
    # __file__ does not work, so we need to reach up the stack for the filename
    filename = inspect.stack()[1][1]
    out.write('%s:%d: Function %s CHECKPOINT\n' % (filename,f.f_lineno,f.f_code.co_name))
