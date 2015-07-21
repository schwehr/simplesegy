#!/usr/bin/env python
"""Debugging utilities."""

import sys

def checkpoint(out=sys.stdout):
    '''Print where this function was called from in a standard format
    that looks like a compiler error'''

    import inspect
    f = inspect.currentframe().f_back
    # __file__ does not work, so we need to reach up the stack for the filename
    filename = inspect.stack()[1][1]
    out.write('%s:%d: Function %s CHECKPOINT\n' % (filename,f.f_lineno,f.f_code.co_name))
