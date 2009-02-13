#!/usr/bin/env python
__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Evaluate how valid a SEGY file is.

@requires: U{Python<http://python.org/>} >= 2.5
@requires: U{epydoc<http://epydoc.sourceforge.net/>} >= 3.0.1
@requires: U{cheetah<http://www.cheetahtemplate.org/>} >= 2.0

@undocumented: __doc__
@since: 2009-Feb-13
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

#import traceback
import os
import sys
#import datetime
#import time

import simplesegy.segy as segy
from simplesegy.cmds import common_opts

def validate_trace(trace,out=sys.stdout,verbose=False):
    v = verbose
    error_count = 0
    errors = []
    t = trace

    if v:
        out.write('\n[trace]\n')

    out.write('line_seq_no ... ')
    if t.line_seq_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('file_seq_no ... ')
    if t.file_seq_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('field_rec_no ... ')
    if t.field_rec_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('trace_no ... ')
    if t.trace_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('esrc_pt_no ... ')
    if t.esrc_pt_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('ensemble_no ... ')
    if t.ensemble_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('trace_no_ensemble ... ')
    if t.trace_no_ensemble >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('trace_id ... ')
    if t.trace_id >= -1: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1



    out.write('vert_sum_no ... ')
    if t.vert_sum_no > 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('horz_stacked_no ... ')
    if t.horz_stacked_no > 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('data_use in (1,2) ... ')
    if t.data_use in (1,2): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.data_use); error_count += 1


    # What is valid?
#    out.write('distance_center ... ')
#    if t.distance_center >= 0: out.write('ok\n')
#    else:
#        out.write('FAIL\n'); error_count += 1

    # What is valid?
#    out.write('recv_grp_elev ... ')
#    if t.recv_grp_elev >= 0: out.write('ok\n')
#    else:
#        out.write('FAIL\n'); error_count += 1

# What is valid?
# surf_elev_src
# src_depth
# elev_rcv_grp
# elev_src

    out.write('water_depth_src ... ')
    if t.water_depth_src >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('water_depth_grp ... ')
    if t.water_depth_grp >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # It doesn't say that 0 is allowed.  Presuming 1 is no scaling
    out.write('scaler_elev_depth in +/- (1,10,100,100,1000) ... ')
    if abs(t.scaler_elev_depth) in (1,10,100,100,1000): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.scaler_elev_depth); error_count += 1

    out.write('scaler_coord in +/- (1,10,100,100,1000) ... ')
    if abs(t.scaler_coord) in (1,10,100,100,1000): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.scaler_coord); error_count += 1

#    # FIX: I haven't yet done 
#    if t.coord_units in (2,3,4):

# x_raw
# y_raw
# grp_x_raw
# grp_y_raw

    out.write('coord_units in (1,2,3,4) ... ')
    if t.coord_units in (1,2,3,4): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.coord_units); error_count += 1

    out.write('wx_vel ... ')
    if t.wx_vel >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sub_wx_vel ... ')
    if t.sub_wx_vel >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('uphole_t_src ... ')
    if t.uphole_t_src >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('uphole_t_grp ... ')
    if t.uphole_t_grp >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

# src_corr
# grp_corr
# tot_static
# lag_t_a
# lag_t_b
# delay

    out.write('mute_start ... ')
    if t.mute_start >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('mute_end ... ')
    if t.mute_end >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('trace_samples ... ')
    if t.trace_samples > 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sample_interval ... ')
    if t.sample_interval >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # 0 is no gain?
    out.write('gain_type ... ')
    if t.gain_type >= 0: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.gain_type); error_count += 1

    out.write('gain_type optional used ... ')
    if t.gain_type < 4: out.write('ok\n')
    else:
        out.write('WARNING (%d)\n' % t.gain_type); error_count += 1

# instr_gain_const
# instr_init_gain

    out.write('correlated in (1,2) ... ')
    if t.correlated in (1,2): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.correlated); error_count += 1

    out.write('sweep_freq_start ... ')
    if t.sweep_freq_start >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_freq_end greater than start ... ')
    if t.sweep_freq_end >= t.sweep_freq_start: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_len ... ')
    if t.sweep_len >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # 0 is no sweep?
    out.write('sweep_type in trace ... ')
    if t.sweep_type in (0,1,2,3,4): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.sweep_type); error_count += 1

    out.write('sweep_taper_len_start ... ')
    if t.sweep_taper_len_start >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_taper_len_end ... ')
    if t.sweep_taper_len_end >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # 0 is no taper?
    out.write('taper_type ... ')
    if t.taper_type in (0,1,2,3): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('alias_filt_freq ... ')
    if t.alias_filt_freq >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

# alias_filt_slope  # can this be +/-?

    out.write('notch_filt_freq ... ')
    if t.notch_filt_freq >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

# notch_filt_slope # how is this bounded?

    out.write('low_cut_freq ... ')
    if t.low_cut_freq >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('high_cut_freq ... ')
    if t.high_cut_freq >= t.low_cut_freq: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

# low_cut_slope   # constraints on these two?
# high_cut_slope

    out.write('year ... ')
    if t.year >= 1920: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.year); error_count += 1

    out.write('day ... ')
    if t.day >= 0 and t.day < 367: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.day); error_count += 1

    out.write('hour ... ')
    if t.hour >= 0 and t.hour < 24: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.day); error_count += 1

    out.write('min ... ')
    if t.min >= 0 and t.min < 60: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.min); error_count += 1

    out.write('sec ... ')
    if t.sec >= 0 and t.sec < 60: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.sec); error_count += 1

    out.write('time_basis in (1,2,3,4) ... ')
    if t.time_basis in (1,2,3,4): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % t.time_basis); error_count += 1

    out.write('trace_weight ... ')
    if t.trace_weight >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

# and we could do more!
# geop_grp_rl_sw1
# geop_grp_tr1
# geop_grp_no_lst_tr
# gap_size
# over_travel

# x_ensemble
# y_ensemble
# post_in_line_no
# post_cross_line_no
# shotpoint
# shotpoint_scaler
# trace_units

# transd_const_mant
# transd_const_exp
# transd_units

# dev_tr_id
# time_scaler
# src_type_orient

# src_e_dir
# src_e_dir_tenths
# src_meas_mantisa
# src_meas_exp
# src_meas_units



    return error_count, errors

def validate(sgy,out=sys.stdout,verbose=False):
    error_count = 0
    errors = []

    v = verbose
    s = sgy
    if v:
        out.write('[validating file]\n')
        out.write('filename = %s\n' % os.path.basename(sgy.filename))

    out.write('Invalid trace trailer present ... ')
    if s.trace_trailer_size > 0: out.write('WARNING (Present)\n')
    else: out.write('ok\n')

    out.write('Byte order ... ')
    if s.swap_byte_order: out.write('WARNING (Backwards)\n')
    else: out.write('ok\n')

    #
    # Text header
    #
    out.write('Text header starts with a C ... ')
    if s.hdr_text[0]=='C': out.write('ok\n')
    else: 
        out.write('FAIL\n')
        error_count += 1

    out.write('job_id positive ... ')
    if s.job_id >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('line_no positive ... ')
    if s.line_no >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('traces_per_ensemble positive ... ')
    if s.traces_per_ensemble >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('aux_traces_per_ensemble positive ... ')
    if s.aux_traces_per_ensemble >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sample_interval positive ... ')
    if s.sample_interval >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('orig_sample_interval positive ... ')
    if s.orig_sample_interval >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('samples_per_trace greater than 0 ... ')
    if s.samples_per_trace > 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('orig_samples_per_trace positive positive ... ')
    if s.orig_samples_per_trace >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sample_format in 1,2,3,4,5, or 8 ... ')
    if s.sample_format in (1,2,3,4,5,  8): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('ensemble_fold positive ... ')
    if s.ensemble_fold >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('trace_sorting in [-1 ... 9]  ... ')
    if s.trace_sorting in range(-1,10): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('vertical_sum ... ')
    if s.vertical_sum > 0 and s.vertical_sum < 32767: out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.vertical_sum); error_count += 1

    out.write('sweep_start positive ... ')
    if s.sweep_start >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_end greater than or equal to start ... ')
    if s.sweep_end >= s.sweep_start: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_len positive ... ')
    if s.sweep_len >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # 0 is no sweep?
    out.write('sweep_type in segy bin header in [0 ... 4] ... ')
    if s.sweep_type in (0,1,2,3,4): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.sweep_type); error_count += 1

    out.write('trace_sweep_channel positive ... ')
    if s.trace_sweep_channel >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # FIX: should check for the sweep that there is enough time for tapers
    out.write('sweep_taper_len_start positive ... ')
    if s.sweep_taper_len_start >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('sweep_taper_len_end positive ... ')
    if s.sweep_taper_len_end >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    # I guess they meant 0 for no taper
    out.write('taper_type is valid ... ')
    if s.taper_type in (0,1,2,3): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('correlated_traces in (1,2) ... ')
    if s.correlated_traces in (1,2): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.correlated_traces); error_count += 1

    out.write('bin_gain_recovered ... ')
    if s.bin_gain_recovered in (0,1): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('amp_recov_meth in (1,2,3,4) ... ')
    if s.amp_recov_meth in (1,2,3,4): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.amp_recov_meth); error_count += 1

    out.write('measurement_system ... ')
    if s.measurement_system in (1,2): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('impulse_polarity in (1,2) ... ')
    if s.impulse_polarity in (1,2): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.impulse_polarity); error_count += 1

    # Assume 0 is no polarity
    out.write('vib_polarity in [0...8] ... ')
    if s.vib_polarity in range(0,9): out.write('ok\n')
    else:
        out.write('FAIL (%d)\n' % s.vib_polarity); error_count += 1

    out.write('seg_y_rev ... ')
    if s.seg_y_rev in (0,1): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('fixed_len_trace_flag ... ')
    if s.fixed_len_trace_flag in (0,1): out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    out.write('num_extended_text_headers ... ')
    if s.num_extended_text_headers >= 0: out.write('ok\n')
    else:
        out.write('FAIL\n'); error_count += 1

    trace_error_count, trace_errors = validate_trace(sgy[0],out,verbose)

    error_count += trace_error_count
    errors += trace_errors 

    return error_count, errors




def main():
    '''
    command line interface for validating a segy file.  Returns 0 if okay.  If the file is bad
    it returns the number of errors
    '''
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]",
                          version="%prog "+__version__+' ('+__date__+')')
    common_opts.add_odec(parser)

    common_opts.add_verbose(parser)

    (options, args) = parser.parse_args()
    o = options
    v = o.verbose

    tot_errors = 0
    for filename in args:
        sgy = segy.Segy(filename, swap_byte_order=o.swap_byte_order, trace_trailer_size=o.trace_trailer_size)
        error_count, errors = validate(sgy,verbose=v)
        tot_errors += error_count

    if tot_errors>0:
        sys.stdout.write('\nERRORS: %d\n'%tot_errors)

    return tot_errors
