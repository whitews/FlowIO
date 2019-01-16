from io import IOBase
from math import log
from operator import and_
from struct import calcsize, unpack
from warnings import warn
import os
import re
from functools import reduce

try:
    # noinspection PyUnresolvedReferences, PyUnboundLocalVariable
    basestring
except NameError:
    # noinspection PyShadowingBuiltins
    basestring = str


class FlowData(object):
    """
    Object representing a Flow Cytometry Standard (FCS) file
    """
    def __init__(self, filename):
        """
        filename: an FCS filename
        """
        if isinstance(filename, basestring):
            try:
                self._fh = open(str(filename), 'rb')
            except IOError:
                raise
        elif isinstance(filename, IOBase):
            self._fh = filename
        else:
            raise TypeError(
                "Filename must be a file path or a file handle " +
                "(either 'file' type or io.IOBase")

        self.cur_offset = 0

        # parse headers
        self.header = self.__parse_header(self.cur_offset)

        # parse text
        self.text = self.__parse_text(
            self.cur_offset,
            self.header['text_start'],
            self.header['text_stop'])

        self.channel_count = int(self.text['par'])
        self.event_count = int(self.text['tot'])

        # parse analysis
        try:
            a_start = self.text['beginanalysis']
        except KeyError:
            a_start = self.header['analysis_start']
        try:
            a_stop = self.text['endanalysis']
        except KeyError:
            a_stop = self.header['analysis_end']
        self.analysis = self.__parse_analysis(self.cur_offset, a_start, a_stop)

        # parse data
        try:
            d_start = int(self.text['begindata'])
        except KeyError:
            d_start = self.header['data_start']
        try:
            d_stop = int(self.text['enddata'])
        except KeyError:
            d_stop = self.header['data_end']

        # account for LMD reporting wrong values for size of the data segment
        lmd = self.__fix_lmd(
            self.cur_offset,
            self.header['text_start'],
            self.header['text_stop'])
        d_stop += lmd
        self.events = self.__parse_data(
            self.cur_offset,
            d_start,
            d_stop,
            self.text)

        try:
            unused_path, self.name = os.path.split(self._fh.name)
        except (AttributeError, TypeError):
            self.name = 'InMemoryFile'

        self._fh.close()

    def __read_bytes(self, offset, start, stop):
        """Read in bytes from start to stop inclusive."""

        self._fh.seek(offset + start)

        return self._fh.read(stop - start + 1)

    def __parse_header(self, offset):
        """
        Parse the FlowData FCS file at the offset (supporting multiple
        data segments in a file
        """
        header = dict()
        header['version'] = float(self.__read_bytes(offset, 3, 5))
        header['text_start'] = int(self.__read_bytes(offset, 10, 17))
        header['text_stop'] = int(self.__read_bytes(offset, 18, 25))
        header['data_start'] = int(self.__read_bytes(offset, 26, 33))
        header['data_end'] = int(self.__read_bytes(offset, 34, 41))
        try:
            header['analysis_start'] = int(self.__read_bytes(offset, 42, 49))
        except ValueError:
            header['analysis_start'] = -1
        try:
            header['analysis_end'] = int(self.__read_bytes(offset, 50, 57))
        except ValueError:
            header['analysis_end'] = -1

        return header

    def __fix_lmd(self, offset, start, stop):
        """
        Handle LMD counting differently then most other FCS data
        """
        text = self.__read_bytes(offset, start, stop)
        if text[0] == text[-1]:
            return 0
        else:
            return -1

    def __parse_text(self, offset, start, stop):
        """return parsed text segment of FCS file"""
        text = self.__read_bytes(offset, start, stop)
        try:
            # try UTF-8 first
            text = text.decode()
        except UnicodeDecodeError:
            # next best guess is Latin-1, if not that either, we throw the exception
            text = text.decode("ISO-8859-1")
        return self.__parse_pairs(text)

    def __parse_analysis(self, offset, start, stop):
        """return parsed analysis segment of FCS file"""
        if start == stop:
            return {}
        else:
            text = self.__read_bytes(offset, start, stop)
            return self.__parse_pairs(text)

    def __parse_data(self, offset, start, stop, text):
        """return array of data segment of FCS file"""
        data_type = text['datatype']
        mode = text['mode']
        if mode == 'c' or mode == 'u':
            raise NotImplementedError(
                "FCS data stored as type \'%s\' is unsupported" % mode
            )

        if text['byteord'] == '1,2,3,4' or text['byteord'] == '1,2':
            order = '<'
        elif text['byteord'] == '4,3,2,1' or text['byteord'] == '2,1':
            order = '>'
        else:
            warn(
                "unsupported byte order %s , using default @" % text['byteord'])
            order = '@'
            # from here on out we assume mode l (list)

        bit_width = []
        data_range = []
        for i in range(1, int(text['par']) + 1):
            bit_width.append(int(text['p%db' % i]))
            try:
                data_range.append(int(text['p%dr' % i]))
            except ValueError:
                #  we found an FCS file where one channel was using
                # exp notation for the int
                data_range.append(int(float(text['p%dr' % i])))

        if data_type.lower() == 'i':
            data = self.__parse_int_data(
                offset,
                start,
                stop,
                bit_width,
                data_range,
                order)
        elif data_type.lower() == 'f' or data_type.lower() == 'd':
            data = self.__parse_float_data(
                offset,
                start,
                stop,
                data_type.lower(),
                order)
        else:  # ascii
            data = self.__parse_ascii_data(
                offset,
                start,
                stop,
                data_type,
                order)
        return data

    def __parse_int_data(self, offset, start, stop, bit_width, d_range, order):
        """Parse out and return integer list data from FCS file"""

        if reduce(and_, [item in [8, 16, 32] for item in bit_width]):
            if len(set(bit_width)) == 1:  # uniform size for all parameters
                # calculate how much data to read in.
                num_items = (stop - start + 1) / calcsize(
                    self.__format_integer(bit_width[0]))

                # unpack to a list
                tmp = unpack(
                    '%s%d%s' %
                    (
                        order, num_items,
                        self.__format_integer(bit_width[0])
                    ),
                    self.__read_bytes(offset, start, stop)
                )

            # parameter sizes are different
            # e.g. 8, 8, 16,8, 32 ... do one at a time
            else:
                log2 = self.__log_factory(2)
                unused_bit_widths = map(int, map(log2, d_range))
                tmp = []
                cur = start
                while cur < stop:
                    for i, cur_width in enumerate(bit_width):
                        bit_mask = self.__mask_integer(
                            cur_width,
                            unused_bit_widths[i])
                        n_bytes = cur_width / 8
                        bin_string = self.__read_bytes(
                            offset, cur,
                            cur + n_bytes - 1)
                        cur += n_bytes
                        val = bit_mask & unpack(
                            '%s%s' %
                            (
                                order,
                                self.__format_integer(cur_width)
                            ),
                            bin_string)[0]
                        tmp.append(val)
        else:  # non standard bit width...  Does this happen?
            warn('Non-standard bit width for data segments')
            return None
        return tmp

    def __parse_float_data(self, offset, start, stop, data_type, order):
        """Parse out and return float list data from FCS file"""
        num_items = (stop - start + 1) / calcsize(data_type)

        tmp = unpack('%s%d%s' % (order, num_items, data_type),
                     self.__read_bytes(offset, start, stop))
        return tmp

    def __parse_ascii_data(self, offset, start, stop, data_type, order):
        """Parse out ascii encoded data from FCS file"""
        num_items = (stop - start + 1) / calcsize(data_type)

        tmp = unpack('%s%d%s' % (order, num_items, data_type),
                     self.__read_bytes(offset, start, stop))
        return tmp

    @staticmethod
    def __parse_pairs(text):
        """return key/value pairs from a delimited string"""
        delimiter = text[0]

        if delimiter != text[-1]:
            warn("text in segment does not start and end with delimiter")

        if delimiter == r'|':
            delimiter = '\|'
        elif delimiter == r'\a'[0]:  # test for delimiter being \
            delimiter = '\\\\'  # regex will require it to be \\

        tmp = text[1:-1].replace('$', '')
        # match the delimited character unless it's doubled
        regex = re.compile('(?<=[^%s])%s(?!%s)' % (
            delimiter, delimiter, delimiter))
        tmp = regex.split(tmp)
        return dict(
            zip(
                [x.lower().replace(
                    delimiter + delimiter, delimiter) for x in tmp[::2]],
                [x.replace(delimiter + delimiter, delimiter) for x in tmp[1::2]]
            )
        )

    @staticmethod
    def __format_integer(b):
        """return binary format of an integer"""
        if b == 8:
            return 'B'
        elif b == 16:
            return 'H'
        elif b == 32:
            return 'I'
        else:
            print("Cannot handle integers of bit size %d" % b)
            return None

    @staticmethod
    def __mask_integer(b, ub):
        """return bit mask of an integer and a bit witdh"""
        if b == 8:
            return 0xFF >> (b - ub)
        elif b == 16:
            return 0xFFFF >> (b - ub)
        elif b == 32:
            return 0xFFFFFFFF >> (b - ub)
        else:
            print("Cannot handle integers of bit size %d" % b)
            return None

    @staticmethod
    def __log_factory(base):
        """factory for various bases or the log function"""
        def f(x):
            return log(x, base)

        return f

    @property
    def channels(self):
        """
        Returns a dictionary of channels, with key as channel number
        and value is a dictionary of the PnN and PnS text
        """
        channels = dict()
        regex_pnn = re.compile("^p(\d+)n$", re.IGNORECASE)

        for i in self.text.keys():
            match = regex_pnn.match(i)
            if not match:
                continue

            channel_num = match.groups()[0]
            channels[channel_num] = dict()

            channels[channel_num]['PnN'] = self.text[match.group()]

            # now check for PnS field, which is optional so may not exist
            regex_pns = re.compile("^p%ss$" % channel_num, re.IGNORECASE)
            for j in self.text.keys():
                match = regex_pns.match(j)
                if match:
                    channels[channel_num]['PnS'] = self.text[match.group()]

        return channels

    def write_fcs(self, filename, extra=None):
        def text_size(text_dict, text_delimiter):
            result = text_delimiter
            for idx in text_dict:
                result += '$%s%s%s%s' % (
                    idx,
                    text_delimiter,
                    text_dict[idx],
                    text_delimiter)
            return len(result), result

        # magic FCS defined positions
        header_text_start = (10, 17)
        header_text_end = (18, 25)
        header_data_start = (26, 33)
        header_data_end = (34, 41)
        header_analysis_start = (42, 49)
        header_analysis_end = (50, 5)

        fh = open(filename, 'wb')
        fh.write('FCS3.1')
        fh.write(' ' * 53)

        # Write TEXT Segment
        text_start = 256  # arbitrarily start at byte 256.
        delimiter = '/'  # use / as our delimiter.

        # Write spaces until the start of the txt segment
        fh.seek(58)
        fh.write(' ' * (text_start - fh.tell()))

        n_channels = int(self.text['par'])
        n_points = len(self.events)
        data_size = 4 * n_channels * n_points  # 4 bytes to hold float

        text = dict()
        text['BEGINANALYSIS'] = '0'
        text['BEGINDATA'] = '0'
        text['BEGINSTEXT'] = '0'
        text['BYTEORD'] = '1,2,3,4'  # little endian
        text['DATATYPE'] = 'F'  # only do float data
        text['ENDANALYSIS'] = '0'
        text['ENDDATA'] = '0'
        text['ENDSTEXT'] = '0'
        text['MODE'] = 'L'  # only do list mode data
        text['NEXTDATA'] = '0'
        text['PAR'] = str(n_channels)
        text['TOT'] = str(n_points)
        for i in range(n_channels):
            text['P%dB' % (i + 1)] = '32'  # float requires 32 bits
            text['P%dE' % (i + 1)] = '0,0'
            text['P%dR' % (i + 1)] = str(max(self.events))
            text['P%dN' % (i + 1)] = str(i)

        if extra is not None:
            for i in extra:
                tmp = i.strip()
                if tmp.lower() not in text and tmp.upper() not in text:
                    val = extra[i].replace(delimiter, delimiter + delimiter)
                    text[i] = val

        i = 1
        size, _ = text_size(text, delimiter)
        prop_size = text_start + ((size % 256) + i) * 256
        text['BEGINDATA'] = prop_size
        text['ENDDATA'] = prop_size + data_size
        data_start = prop_size
        data_end = prop_size + data_size - 1
        size, text_segment = text_size(text, delimiter)
        text_end = text_start + size - 1

        fh.write(text_segment)
        fh.write(' ' * (data_start - fh.tell()))
        fh.write(str(float(i) for i in self.events))

        fh.seek(header_text_start[0])
        fh.write(str(text_start))
        fh.seek(header_text_end[0])
        fh.write(str(text_end))

        fh.seek(header_data_start[0])
        if len(str(data_end)) < (header_data_end[1] - header_data_end[0]):
            fh.write(str(data_start))
            fh.seek(header_data_end[0])
            fh.write(str(data_end))
        else:
            fh.write(str(0))
            fh.seek(header_data_end[0])
            fh.write(str(0))

        fh.seek(header_analysis_start[0])
        fh.write(str(0))
        fh.seek(header_analysis_end[0])
        fh.write(str(0))

        fh.close()

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name
