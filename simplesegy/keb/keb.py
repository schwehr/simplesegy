#!/usr/bin/env python

"""Read Knudsen KEL Binary KEL B9 format.

Described in D101-03574-Rev1.1 - B9 format.pdf.
"""

import argparse
import datetime
import mmap
import os
import re
import struct
import sys
import time
import traceback
import warnings


header_re_str = r"""KEB\s*(?P<software>[-A-Z0-9]*)\s*(?P<version>V[0-9]*\.[0-9]*)\s*(?P<compression>Huffman)?"""
header_re = re.compile(header_re_str)
DATA_START = 40


class KebIterator:
    """Iterate across the traces of a Knudsen KEB."""

    def __init__(self, keb):
        self.keb = keb
        self.cur_pos = DATA_START # Always starts at 40
        self.size = keb.size
        self.data = keb.data
        self.compression = keb.compression

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.cur_pos > self.size-1:
            raise StopIteration
        record = Record(self.data, self.cur_pos, self.compression)
        self.cur_pos += len(record)
        return record


class Ping:
    '''Record type 0xb9 (185 decimal)'''
    def __init__(self, data, record_size, offset=0, compression=None):

        # print 'offset:',offset,'record_size:',record_size
        self.data = data[offset:offset+record_size]

        if compression is not None:
            # sys.exit('ERROR: Decompression not yet implemented for type "%s"' % compression)
            # http://www.inference.phy.cam.ac.uk/mackay/python/compression/huffman/
            # http://code.activestate.com/recipes/576603/

            # http://books.google.com/books?id=GxKWdn7u4w8C&pg=PA456&lpg=PA456&dq=python+huffman&source=bl&ots=M6u8cXxvu_&sig=DWYdLasXkw06devvQFtKorEu3c4&hl=en&ei=WFacSYK6KteitgfM6_3fBA&sa=X&oi=book_result&resnum=1&ct=result#PPA462,M1
            warnings.warn('Huffman not yet decoded')
            return


        self.record_id = struct.unpack('B',self.data[0])[0]
        #print 'record_id', self.record_id, hex(self.record_id)
        #if 0xb9!=self.record_id:
        #    print 'WARNING: something is wrong!!!'

        self.record_length = struct.unpack('<H',self.data[1:3])[0]
        #print 'record_length',self.record_length

        self.record_num = struct.unpack('<H',self.data[3:5])[0]
        self.num_channels = struct.unpack('B',self.data[5])[0]
        self.reserved_bytes = struct.unpack('<H',self.data[6:8])[0] # should be 0

        self.day  = struct.unpack('B' ,self.data[8])[0]
        self.mon  = struct.unpack('B' ,self.data[9])[0]
        #self.year = struct.unpack('<H',self.data[10:12])[0]
        #print 'year:',self.year

        self.hour = struct.unpack('B' ,self.data[12])[0]
        self.min  = struct.unpack('B' ,self.data[13])[0]
        self.sec  = struct.unpack('B' ,self.data[14])[0]
        self.msec = struct.unpack('<H',self.data[15:17])[0]

        self.units = struct.unpack('B',self.data[17])[0]
        self.sound_speed = struct.unpack('<H',self.data[18:20])[0]


    def __unicode__(self):
        return '{record_id} {record_length} {record_num} {num_channels} ({year}-{mon}-{day} {hour}:{min}:{sec}'.format(**self.__dict__)

    def __str__(self):
        return self.__unicode__()


class Record:
    '''Includes both the payload record and the preamble'''
    def __init__(self,data,offset=0, compression=None):
        self.data = data
        self.offset = offset
        self.compression = compression

        self.type_code = struct.unpack('B',data[offset])[0]
        #print 'typecode',self.type_code, hex(self.type_code)

        self.record_offset = struct.unpack('<I',data[offset+1:offset+5])[0]
        #print 'record_offset',self.record_offset

        self.record_size = struct.unpack('<I',data[offset+5:offset+9])[0]
        #print 'record_size',self.record_size

        self.event_mark = struct.unpack('<B',data[offset+9])[0]
        #print 'event_mark',self.event_mark, hex(self.event_mark)

        if 0xb9 == self.type_code:
            self.payload = Ping(data,
                                record_size = self.record_size,
                                offset = self.offset + 10,
                                #offset = self.offset,
                                compression = self.compression)
        else:
            print 'unknown/unhandled type_code of',self.type_code,hex(self.type_code)


    def __unicode__(self):
        return 'KEB Record: %s(%d) %d %d %s' % (
            hex(self.type_code),
            self.type_code,
            self.record_offset,
            self.record_size,
            self.event_mark
            )

    def __str__(self):
        return self.__unicode__()

    def __len__(self):
        return self.record_size+10





class Keb:
    def __init__(self, filename):
        self.filename = filename
        tmpFile = file(filename,'r+')
        self.size = os.path.getsize(filename)
        self.data = mmap.mmap(tmpFile.fileno(),self.size,access=mmap.ACCESS_READ)
        data = self.data

        file_type_data = str(data[0:40])
        header_match = header_re.search(file_type_data)
        #print 'header_match',header_match
        self.software = header_match.group('software')
        self.version = header_match.group('version')
        self.compression = header_match.group('compression')

#         for i in range(1000):
#             start = i
#             end   = i + 2
#             d = data[start:end]
#             M = struct.unpack('B',d[0])[0]
#             m = struct.unpack('b',d[0])[0]

#             a = struct.unpack('>H',d)[0]
#             b = struct.unpack('<H',d)[0]
#             c = struct.unpack('>h',d)[0]
#             D = struct.unpack('<h',d)[0]

#             print i,'yr',start,end,d,'->',a,b,c,D,m,hex(m),M,hex(M),d[0]

#         sys.exit('EARLY')


    def __iter__(self):
        return KebIterator(self)

    def __unicode__(self):
        return 'Knudesen KEB B9: software %s, version: %s compression: %s' % (
            self.software,
            self.version,
            self.compression
            )

    def __str__(self):
        return(self.__unicode__())

# k = Keb('Marianas_Line_013.keb')
# print 'str',str(k)

# for i,rec in enumerate(k):
#     if i>50:
#         sys.exit('EARLY out of the loop')
#     print 'REC',str(rec)
#     #print '  PING',str(rec.payload)
#     #o = file ('ping-compressed-%03d.bin' %i,'w+')
#     #o.write(rec.payload.data)
#     #print '  PING',str(rec.payload)
#     file('ping%03d.bin' % i,'w').write(rec.payload.data)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('filenames', metavar='N', type=str, nargs='+',
                 help='Files to get info about.')
  args = parser.parse_args()

  for filename in args.filenames:
    print filename
    keb = Keb(filename)
    for rec_num, rec in enumerate(keb):
      print rec


if __name__ == '__main__':
    main()
