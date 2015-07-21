#!/usr/bin/env python
"""Convert a Segy object to a text representation.  Fancier than just __str__ and __unicode__."""
import simplesegy.segy as segy
from simplesegy.utils.debugging import checkpoint

def convert(out, sgy,
            summary = False,
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

    if summary:
        if v:
            out.write('\n[summary]')
        metadata = sgy.trace_metadata()
        # FIX: pretty up!
        out.write('%s\n' % str(metadata))

    if text_header:
        if v:
            out.write('\n[text header]\n')
        text = sgy.hdr_text
        for i in range (len(text) / 80):
            out.write(text[i*80:(i+1)*80])
            out.write('\n')

    if bin_header:
        if v:
            out.write('\n[bin header]\n')
        for item in segy.segy_bin_header_lut:
            out.write('%s = %s\n' % (item, sgy.__dict__[item]))

    if trace_num is not None:
        if v:
            out.write('\n[trace %d]\n' % trace_num)
        t = sgy[trace_num]

        if len(trace_fields)==0:
            # Dump them all
            for field in segy.trace_field_lut:
                out.write('%s = %s\n' % (field,t.__getattr__(field)))
        else:
            if v:
                out.write('# ')
                for field in trace_fields:
                    out.write('%s,' % field)
                out.write('\n')
            for field in trace_fields:
                out.write('%s = %s\n' % (field,t.__getattr__(field)))

    #checkpoint()
    if all_traces:
        # Use a more compact format
        #checkpoint()
        if v:
            out.write('\n[traces]\n')

        if len(trace_fields)==0:
            #checkpoint()
             trace_fields = ('x','y', ) + tuple(segy.trace_field_lut.keys()) # 'time',
             if v:
                 out.write('# Fields: ')
                 out.write(', '.join( trace_fields ) )
                 out.write('\n')
             for i,t in enumerate(sgy):
                 out.write('5%d:' % i)
                 out.write(', '.join( [ str(t.__getattr__(field)) for field in trace_fields] ) )
                 out.write('\n')
        else:
             #checkpoint()
             if v:
                 out.write('# trace: ')
                 out.write(', '.join( trace_fields ) )
                 out.write('\n')
             for i,t in enumerate(sgy):
                 #print i
                 out.write('%5d: ' % i)
                 out.write(', '.join( [ str(t.__getattr__(field)) for field in trace_fields] ) )
                 out.write('\n')


