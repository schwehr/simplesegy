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
import traceback
import os
import mmap   # load the file into memory directly so it looks like a big array
import struct # Unpacking of binary data
import datetime
import time
import codecs

from simplesegy.utils.debugging import checkpoint

class SegyError(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class SegyTraceError(SegyError):
    pass

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
        'x_raw':('>i',72,76),
        'y_raw':('>i',76,80),
        'grp_x_raw':('>i',80,84),
        'grp_y_raw':('>i',84,88),
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
        'low_cut_slope':('>h',152,154),
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

def rawpos_to_geographic(trace,field_name,verbose):
        v = verbose
        scalar = trace.scaler_coord
        units = trace.coord_units

        coord = trace.__getattr__(field_name)

        if scalar not in (-10000, -1000, -100, -10, 0 , 10, 100, 1000, 10000):
            raise SegyTraceError('Invalid scalar of %d' % scalar)

        if units>4:
            sys.stderr.write('forcing units to 3 for %s.  Is this odd odec?\n'% units)
            units=3

        if units==0:
            if v: 
                sys.stderr.write('forcing units to 3 for a 0\n')
            units=3

        if units==1: # Length (meters or feet)
            pass # Nothing to do

        elif units==2: # Seconds of arc
            coord /= 3600.
            if scalar>0: # Multiplier
                coord *= scalar
            if scalar<0: # Divisor
                coord /= abs(scalar)

        elif units==3: # Decimal degrees - FIX: is this always a float or just for ODEC?
            if self.swap_byte_order:
                fmt = '<2f'
            else:
                fmt = '>2f'
            # It's an IEEE float, have to decode
            start = trace_field_lut[field_name][1]
            end = trace_field_lut[field_name][2]
            assert (0!=start)
            assert (0!=end)
            coord = struct.unpack(fmt,trace.data[trace.offset+start:trace.offset+end])
            if scalar>0: # Multiplier
                coord *= scalar
            if scalar<0: # Divisor
                coord /= abs(scalar)

        elif units==4: # Degrees, minutes, seconds
            print 'units 4 debugging.  incoming values: ',x,y,scalar
            assert False
        #else:
        #    raise SegyError('Invalide or unsupported coordinate units: %d' % units)

        return coord


class Trace:
    '''As defined in Segy Rev 1
    @todo: make these delayed decodes as most will never be used
    '''

    def __init__(self,data,
                 sample_format=3,data_offset=0, 
                 swap_byte_order=False, 
                 trace_trailer_size=0, 
                 verbose=False):
        '''
        @param trace_trailer_size: hack for ODEC
        '''
        offset = self.offset = data_offset
        self.verbose = verbose
        self.swap_byte_order = swap_byte_order

        self.sample_format=sample_format
        self.sample_size = data_format_bytes_per_sample[sample_format]
        self.trace_trailer_size = trace_trailer_size

        # have to prefetch this one attribute
        if swap_byte_order:
            self.trace_samples = struct.unpack('<h',data[offset+114:offset+116])[0]
        else:
            self.trace_samples = struct.unpack('>h',data[offset+114:offset+116])[0]

        if self.trace_samples < 0:
            raise SegyTraceError('Bad trace length.  Corrupt file?')

        self.size = self.sample_size * self.trace_samples + 240 + trace_trailer_size # 240 For binary header

        self.data = data

    def get_trace_data(self):
        return self.data[self.offset:self.offset+self.size]

    def __unicode__(self):
        return unicode(self.position_geographic())

    def __str__(self):
        return self.__unicode__()

    def __len__(self):
        'Number of bytes, NOT the number of samples.'
        return self.size

    def __getattr__(self,name):
        if name=='samples':
            if self.sample_format in data_format_struct:
                code = data_format_struct[self.sample_format]
                base = self.offset+240
                end = base + self.sample_size * self.trace_samples
                endian = '>'
                if self.swap_byte_order:
                    endian = '<'
                fmt = '%s%d%s' % (endian,self.trace_samples, code[1:])
                self.samples = struct.unpack(fmt, self.data[base:end]) 
                return self.samples

        if name in trace_field_lut:
            struct_code,start,end = trace_field_lut[name]
            if self.swap_byte_order:
                struct_code = '<' + struct_code[1:]
            val = struct.unpack(struct_code,self.data[self.offset+start:end+self.offset])[0]
            self.__dict__[name] = val
            return val

        #
        # Special aggregate names
        # 
        if name == 'x':
            return rawpos_to_geographic(self, 'x_raw', self.verbose)
        if name == 'y':
            return rawpos_to_geographic(self, 'y_raw', self.verbose)

        if name == 'pos':
            return self.x,self.y #self.position_geographic()

        if name == 'time':
            return self.datetime()

        raise AttributeError(name)

    def datetime(self):
        '''
        @todo: factor in time basis
        '''
        julian_day = self.day
        t = time.strptime('%4d %03d' % (self.year,julian_day),'%Y %j')
        return datetime.datetime(self.year,t.tm_mon,t.tm_mday,self.hour,self.min,self.sec)

    def position_geographic(self):
        '''
        I think the knudsen positions of dividing by 3600000 is not correct for the coord_units
        @bug: this will fail near 0,0
        @todo: pay attention to coord_units'''

        return self.x,self.y


class SegyIterator:
    'Iterate across the traces of a SEGY file'
    def __init__(self, segy):
        self.segy = segy
        self.cur_pos = segy.trace_start
        self.size = segy.size
        self.data = segy.data
        self.sample_format = segy.sample_format
        self.trace_trailer_size = segy.trace_trailer_size # ODEC hack
        self.trace_count=0

        self.swap_byte_order = segy.swap_byte_order

    def __iter__(self):
        return self

    def __next__(self):
        if self.cur_pos > self.size-1:
            raise StopIteration
        trace = Trace(self.data,
                      self.sample_format,
                      self.cur_pos,swap_byte_order = self.swap_byte_order, 
                      trace_trailer_size = self.trace_trailer_size)

        self.cur_pos += len(trace)
        self. trace_count += 1
        return trace

    def next(self):
        'python 2.x compat'
        return self.__next__()

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
    def __init__(self, filename, swap_byte_order=False, trace_trailer_size=0):
        '''
        @param trace_trailer: bytes at the end of each trace.  This is for ODEC (which uses 320) and is not standard SEGY
        @param swap_byte_order: ODEC uses the wrong byte order
        '''
        self.swap_byte_order = swap_byte_order # For bad venders

        self.filename = filename
        tmpFile = file(filename,'r+')
        self.size = os.path.getsize(filename)
        self.data = mmap.mmap(tmpFile.fileno(),self.size,access=mmap.ACCESS_READ)
        data = self.data
        self.trace_trailer_size = trace_trailer_size
        self.trace_indices = [] # Lookup table of trace headers

        self.hdr_text = decode_text(data[0:3200]) # Initial ASCII or EBCDIC header
        # Next comes a 400 byte binary header
        #self.hdr = {}
        for name in segy_bin_header_lut:
            struct_code,start,end = segy_bin_header_lut[name]
            if swap_byte_order:
                struct_code = '<'+struct_code[1:]
            val = struct.unpack(struct_code,self.data[start:end])[0]
            self.__dict__[name] = val

        self.sample_size = data_format_bytes_per_sample[self.sample_format]

        file_pos = 3600
        self.extended_text_hdrs = []
        for i in range (self.num_extended_text_headers):
            self.extended_text_hdrs.append(decode_text(data[file_pos:file_pos+3200]))
            file_pos += 3200

        self.trace_start = file_pos

        # HACK for ODEC bad byte order
        if self.sample_format not in data_formats_description:
            hdr_tbl = segy_bin_header_lut['sample_format']
            fmt = struct.unpack('<h',self.data[hdr_tbl[1]:hdr_tbl[2]])[0]
            if fmt in data_formats_description:
                self.sample_format = fmt
                #sys.stderr.write('WARNING: vendor byte order problem with sample_format')
                raise SegyError('Bad byte order file: this is not compliant SEGY.  Consider trying swapped byte order')
            else:
                raise SegyError('Bad sample_format of %s (or %s if bad byte order)' % (self.sample_format, fmt))


    def __len__(self):
        if 1==self.fixed_len_trace_flag:
            byte_count = self.size - self.trace_start
            return byte_count / self.trace_size()
        for i,trace in enumerate(sgy):
            pass
        return i
            
    def trace_size(self):
        'Returns trace size or None if variable length'
        if self.fixed_len_trace_flag==1:
            return self.samples_per_trace*self.sample_size + 240 + self.trace_trailer_size
        elif self.fixed_len_trace_flag==0:
            return None
        raise SegyError('Unknown trace size code of %s' % self.fixed_len_trace_flag)

    def is_valid(self):
        'Test to see if we can tell that this is valid'
        assert(False)

    def __getitem__(self, key):
        if not isinstance(key,int):
            raise AttributeError(key)

        if self.fixed_len_trace_flag==1:
            trace_size = self.samples_per_trace*self.sample_size + 240 + self.trace_trailer_size
            start = self.trace_start + ( trace_size * key)
            return Trace(self.data, self.sample_format, start, swap_byte_order=self.swap_byte_order, trace_trailer_size = self.trace_trailer_size)
        else:
            # Variable length: we have to look at each trace - more work
            if len(self.trace_indices) == 0:
                self.trace_indices.append(self.trace_start)
            if key < len(self.trace_indices):
                return Trace(self.data, self.sample_format, self.trace_indices[key], swap_byte_order=self.swap_byte_order, trace_trailer_size = self.trace_trailer_size)
            cur = len(self.trace_indices)-1
            while (cur < key):
                trace = Trace(self.data, self.sample_format, self.trace_indices[cur], swap_byte_order=self.swap_byte_order, trace_trailer_size = self.trace_trailer_size)
                cur += 1
                self.trace_indices.append(self.trace_indices[cur-1] + len(trace))
                if cur == key: 
                    return trace


    def __unicode__(self):
        fmtnum = self.sample_format
        
        return os.path.basename('%s %s' % (self.filename,fmtnum))

    def __str__(self):
        return self.__unicode__()

    def trace_metadata(self):
        x_min=None
        x_max=None
        y_min=None
        y_max=None
        t_min=None
        t_max=None

        try:
            for tracecount,t in enumerate(self):

                # Watch out for bad times!
                if not t_min and t.year != 0: 
                    t_min = t.datetime()
                x,y = t.position_geographic()
                if not x_min or x<x_min: x_min = x
                if not x_max or x>x_max: x_max = x
            
                if not y_min or y<y_min: y_min = y
                if not y_max or y>y_max: y_max = y

                if t.year != 0:
                    t_max = t.datetime()
        except SegyTraceError, e:
            sys.stderr.write('    Exception:' + str(type(Exception))+'\n')
            sys.stderr.write('    Exception args:'+ str(e)+'\n')
        except ValueError, e:
            sys.stderr.write('    Exception:' + str(type(Exception))+'\n')
            sys.stderr.write('    Exception args:'+ str(e)+'\n')
        
        return (x_min,y_min),(x_max,y_max),(t_min,t_max)

    def __iter__(self):
        return SegyIterator(self)
