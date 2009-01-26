__author__    = 'Kurt Schwehr'
__version__   = '$Revision: 4799 $'.split()[1]
__revision__  = __version__ # For pylint
__date__ = '$Date: 2006-09-25 11:09:02 -0400 (Mon, 25 Sep 2006) $'.split()[1]
__copyright__ = '2009'
__license__   = 'Python'
__contact__   = 'kurt at ccom.unh.edu'

__doc__ ='''
Read SEG-Y Rev 0 and 1.  Partially derived from Kurt Schwehr's segy-py / seismic-py.

@requires: U{Python<http://python.org/>} >= 2.5

@undocumented: __doc__
@since: 2009-Jan-25
@status: under development
@organization: U{CCOM<http://ccom.unh.edu/>} 
'''

import sys
import os
import mmap   # load the file into memory directly so it looks like a big array
import struct # Unpacking of binary data
import datetime
import time
import codecs

class SegyError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

data_formats_description = {
    1: "4-byte IBM floating point",
    2: "4-byte, twos complement integer",
    3: "2-byte, twos complement integer",
    4: "4-byte, fixed-point with gain(obsolete)",
    5: "4-byte IEEE floating-point",
    6: "Not currently used",
    7: "Not currently used",
    8: "1-byte, twos complement integer"
    }

data_format_bytes_per_sample = {
    1: 4,
    2: 2,
    3: 2,
    4: 4,
    5: 4,
    8: 1,
    }

struct_int_codes = { 1: '>b', 2: '>h', 4: '>i', 8: '>q' }

data_format_struct = {
#    1: None, # What to do for IBM floats?
    2: struct_int_codes[4],
    3: struct_int_codes[2],
#    4: None, # structintCode[4],  * something...
    5: "f", # float
#    6: None,
#    7: None,
    8: struct_int_codes[1],
    }


coord_units_desc = {
     1: 'Length (meters or feet)',
     # An arc second is therefore an angular measurement that equals
     # 1/60th of an arc minute, or 1/3600 of a single degree of arc.
     2: 'Seconds of arc',
     3: 'Decimal degrees',
     4: 'Degrees, minutes, seconds' # (DMS)Note: To encode +-DDDMMSS bytes 89-90 equal = +-DDD*104 + MM*102 + SS with bytes 71-72 set to 1; To encode +-DDDMMSS.ss bytes 89-90 equal = +-DDD*106 + MM*104 + SS*102 with bytes 71-72 set to -100.',
    }

trace_field_lut = {
        'line_seq_no':('>i',0,4),
        'file_seq_no':('>i',4,8),
        'field_rec_no':('>i',8,12),
        'trace_no':('>i',12,16),
        'esrc_pt_no':('>i',16,20),
        'ensemble_no':('>i',20,24),
        'trace_no_ensemble':('>i',24,28),
        'trace_id':('>h',28,30),

        'vert_sum_no':('>h',30,32),
        'horz_stacked_no':('>h',32,34),
        'data_use':('>h',34,36),
     
        'distance_center':('>i',36,40),
        'recv_grp_elev':('>i',40,44),
        'surf_elev_src':('>i',44,48),
        'src_depth':('>i',48,52),
        'elev_rcv_grp':('>i',52,56),
        'elev_src':('>i',56,60),

        'water_depth_src':('>i',60,64),
        'water_depth_grp':('>i',64,68),
        'scaler_elev_depth':('>h',68,70),
        'scaler_coord':('>h',70,72),
        'x':('>i',72,76),
        'y':('>i',76,80),
        'grp_x':('>i',80,84),
        'grp_y':('>i',84,88),
        'coord_units':('>h',88,90),

        'wx_vel':('>h',90,92),
        'sub_wx_vel':('>h',92,94),
        'uphole_t_src':('>h',94,96),
        'uphole_t_grp':('>h',96,98),
        'src_corr':('>h',98,100),
        'grp_corr':('>h',100,102),
        'tot_static':('>h',102,104),
        'lag_t_a':('>h',104,106),
        'lag_t_b':('>h',106,108),
        'delay':('>h',108,110),


        'mute_start':('>h',110,112),
        'mute_end':('>h',112,114),
        'trace_samples':('>h',114,116),
        'sample_interval':('>h',116,118),
        'gain_type':('>h',118,120),

        'instr_gain_const':('>h',120,122),
        'instr_init_gain':('>h',122,124),
        'correlated':('>h',124,126),
        'sweep_freq_start':('>h',126,128),
        'sweep_freq_end':('>h',128,130),
        'sweep_len':('>h',130,132),
        'sweep_type':('>h',132,134),

        'sweep_taper_len_start':('>h',134,136),
        'sweep_taper_len_end':('>h',136,138),
        'taper_type':('>h',138,140),

        'alias_filt_freq':('>h',140,142),
        'alias_filt_slope':('>h',142,144),
        'notch_filt_freq':('>h',144,146),
        'notch_filt_slope':('>h',146,148),
        'low_cut_freq':('>h',148,150),
        'high_cut_freq':('>h',150,152),
        'low_cut_slope':('>h',154,154),
        'high_cut_slope':('>h',154,156),
        'year':('>h',156,158),
        'day':('>h',158,160),
        'hour':('>h',160,162),
        'min':('>h',162,164),
        'sec':('>h',164,166),
        'time_basis':('>h',166,168),

        'trace_weight':('>h',168,170),
        'geop_grp_rl_sw1':('>h',170,172),
        'geop_grp_tr1':('>h',172,174),
        'geop_grp_no_lst_tr':('>h',174,176),
        'gap_size':('>h',176,178),
        'over_travel':('>h',178,180),

        'x_ensemble':('>i',180,184),
        'y_ensemble':('>i',184,188),
        'post_in_line_no':('>i',188,192),
        'post_cross_line_no':('>i',192,196),
        'shotpoint':('>i',196,200),
        'shotpoint_scaler':('>h',200,202),
        'trace_units':('>h',202,204),

        'transd_const_mant':('>i',204,208),
        'transd_const_exp':('>h',208,210),
#         'transdconst':('>h',205,210,'transduction constant - the multiplicative constant used to convert the data trace samples to the transduction units (specified in trace header bytes 211-212).  the constant is encoded as a four-byte, two\'s complement integer (bytes 205-208) which is the mantissa and a two-byte, two\'s complement integer (bytes 209-210) which is the power of ten exponent (i.E100. bytes 20550-208 * 10**bytes 209-210). ',
        'transd_units':('>h',210,212),

        'dev_tr_id':('>h',212,214),
        'time_scaler':('>h',214,216),
        'src_type_orient':('>h',216,218),

        # fix, is this the right split for srcedir and srcedirtenths?
        'src_e_dir':('>i',218,222),
        'src_e_dir_tenths':('>h',222,224),
        'src_meas_mantisa':('>i',224,228),
        'src_meas_exp':('>h',228,230),
        'src_meas_units':('>h',230,232),
        #'unassigned233':('>h',232,240),
}
'''field name: struct code, start, end'''


class Trace:
    '''As defined in Segy Rev 1
    @todo: make these delayed decodes as most will never be used
    '''

    def __len__(self):
        return self.size

    def __getattr__(self,name):
        if name=='samples':
            if self.sample_type in data_format_struct:
                samples = []
                code = data_format_struct[self.sample_type]
                base = self.offset+240
                for i in range(self.TraceSamples):
                    start = base+i*self.sample_size
                    end = start+self.sample_size
                    samples.append( struct.unpack(code,self.data[start:end])[0] )
                self.samples = samples # Cache it
                return samples
        if name in trace_field_lut:
            struct_code,start,end = trace_field_lut[name]
            val = struct.unpack(struct_code,self.data[self.offset+start:end+self.offset])[0]
            self.__dict__[name] = val
            return val
        raise AttributeError, name

    def datetime(self):
        '''
        @todo: factor in time basis
        '''
        julian_day = self.day
        t = time.strptime('%4d%03d' % (self.year,julian_day),'%Y%j')
        return datetime.datetime(self.year,t.tm_mon,t.tm_mday,self.hour,self.min,self.sec)


    def __init__(self,data,sample_type=3,data_offset=0):
        #hdr = {}
        offset = self.offset = data_offset

        self.sample_type=sample_type
        self.sample_size = data_format_bytes_per_sample[sample_type]

        # have to prefetch this one attribute
        self.trace_samples = struct.unpack('>h',data[offset+114:offset+116])[0]

        self.size = self.sample_size * self.trace_samples + 240 # 240 For binary header
        self.data = data

    def position_raw(self):
        return self.x,self.y

    def position_geographic(self):
        '''
        I think the knudsen positions of dividing by 3600000 is not correct for the coord_units
        @bug: this will fail near 0,0
        @todo: pay attention to coord_units'''
        x = self.x / 3600.
        y = self.y / 3600.
        if abs(x) > 180 or abs(y)>90:
            x /= 1000.
            y /= 1000.
        return  x,y

class SegyIterator:
    'Iterate across the traces of a SEGY file'
    def __init__(self, segy):
        self.segy = segy
        self.cur_pos = segy.trace_start
        self.size = segy.size
        self.data = segy.data
        self.sample_type = segy.sample_format

    def __iter__(self):
        return self

    def next(self):
        if self.cur_pos > self.size-1:
            raise StopIteration
        trace = Trace(self.data,self.sample_type,self.cur_pos)
        self.cur_pos += len(trace)
        return trace

def decode_text(in_data):
    '''Decode ASCII or EBCDIC text block'''
    first_char = ord(in_data[0])
    if first_char == 67:
        return in_data # ASCII
    if first_char == 195:
        return codecs.decode(in_data,'cp037') # EBCDIC

    raise SegyError('Can not decode header bytes')

def parse_text_header(text,strip_c=False):
    'Parse the standard text header text with C## in 80 character line'
    fields=[]

    if strip_c:
        for i in range(0,3200-80,80):
            fields.append(text[i+4:i+80])
    else:
        for i in range(0,3200-80,80):
            fields.append(text[i:i+80])
    return fields

segy_bin_header_lut = {
        'job_id':('>i',3200,3204),
        'line_no':('>i',3204,3208),
        'reel_no':('>i',3208,3212),
        'traces_per_ensemble':('>h',3212,3214),
        'aux_traces_per_ensemble':('>h',3214,3216),
        'sample_interval':('>h',3216,3218),
        'orig_sample_interval':('>h',3218,3220),
        'samples_per_trace':('>h',3220,3222),
        'orig_samples_per_trace':('>h',3222,3224),
        'sample_format':('>h',3224,3226),
        'ensemble_fold':('>h',3226,3228),
        'trace_sorting':('>h',3228,3230),
        'vertical_sum':('>h',3230,3232),
        'sweep_start':('>h',3232,3234),
        'sweep_end':('>h',3234,3236),
        'sweep_len':('>h',3236,3238),
        'sweep_type':('>h',3238,3240),
        'trace_sweep_channel':('>h',3240,3242),
        'sweep_taper_len_start':('>h',3242,3244),
        'sweep_taper_len_end':('>h',3244,3246),
        'taper_type':('>h',3246,3248),
        'correlated_traces':('>h',3248,3250),
        # note, yes and no are different between the two!
        'bin_gain_recovered':('>h',3250,3252),
        'amp_recov_meth':('>h',3252,3254),
        'measurement_system':('>h',3254,3256),
        'impulse_polarity':('>h',3256,3258),
        'vib_polarity':('>h',3258,3260),
        #'unassigned3261', [3260,3500]
        'seg_y_rev':('>h',3500,3502),
        'fixed_len_trace_flag':('>h',3502,3504),
        'num_extended_text_headers':('>h',3504,3506),
}
''' name of the attribute: struct code, start, end.  No offset needed'''

class Segy:
    def __init__(self, filename):
        tmpFile = file(filename,'r+')
        self.size = os.path.getsize(filename)
        self.data = mmap.mmap(tmpFile.fileno(),self.size,access=mmap.ACCESS_READ)
        data = self.data

        self.hdr_text = decode_text(data[0:3200]) # Initial ASCII or EBCDIC header

        # Next comes a 400 byte binary header
        #self.hdr = {}
        for name in segy_bin_header_lut:
            struct_code,start,end = segy_bin_header_lut[name]
            val = struct.unpack(struct_code,self.data[start:end])[0]
            self.__dict__[name] = val

        file_pos = 3600
        self.extended_text_hdrs = []
        for i in range (self.num_extended_text_headers):
            self.extended_text_hdrs.append = decode_text(data[file_pos:file_pos+3200])
            file_pos += 3200

        self.trace_start = file_pos

    def trace_metadata(self):
        x_min=None
        x_max=None
        y_min=None
        y_max=None
        t_min=None
        for t in self:
            if not t_min: t_min = t.datetime()
            x,y = t.position_geographic()
            if not x_min or x<x_min: x_min = x
            if not x_max or x>x_max: x_max = x

            if not y_min or y<y_min: y_min = y
            if not y_max or y>y_max: y_max = y

        t_max = t.datetime()
        return (x_min,y_min),(x_max,y_max),(t_min,t_max)

    def __iter__(self):
        return SegyIterator(self)
