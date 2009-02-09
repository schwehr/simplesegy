#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
convert a Segy object to a text representation.  Fancier than just __str__ and __unicode__

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1

@undocumented: __doc__
@since: 2009-Feb-09
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

#import os
import simplesegy.segy as segy

def convert(out, sgy, 
            text_header=False,
            bin_header=False, 
            all_traces=False,
            trace_fields=None,
            trace_num=None,
            verbose=False):
    '''
    @param out: file like object to write to
    @segy: Segy instance
    '''
    v = verbose

    if text_header:
        if v:
            out.write('[text header]\n')
        text = sgy.hdr_text
        for i in range (len(text) / 80):
            out.write(text[i*80:(i+1)*80])
            out.write('\n')

    if bin_header:
        if v:
            out.write('[bin header]\n')
        for item in segy.segy_bin_header_lut:
            out.write('%s = %s\n' % (item, sgy.__dict__[item]))

    if trace_num is not None:
        if v:
            out.write('[trace %d]\n' % trace_num)
        t = sgy[trace_num]

        if len(trace_fields)==0:
            # Dump them all
            #print 'FIX: segy.trace_field_lut', segy.trace_field_lut
            for field in segy.trace_field_lut:
                print 'field:', field
                out.write('%s = %s\n' % (field,t.__getattr__(field)))
        else:
            for field in trace_fields:
                out.write('%s = %s\n' % (field,t.__dict__[field]))

    if all_traces:
        # Use a more compact format
         if len(trace_fields)==0:
            for i,t in enumerate(sgy):
                out.write('5%d:' % i)
                for field in segy.trace_field_lut:
                    out.write('%s, ' % (field,t.__dict__[field]))
                out.write('\n')
         else:
             for i,t in enumerate(sgy):
                 out.write('5%d:' % i)
                 for field in trace_fields:
                     out.write('%s, ' % (t.__dict__[field]))
                 out.write('\n')

            
