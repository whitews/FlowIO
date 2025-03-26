import array
from operator import and_
from pathlib import Path
from struct import calcsize, iter_unpack
from warnings import warn
import os
import re
import numpy as np
from functools import reduce
from .create_fcs import create_fcs
from .exceptions import FCSParsingError, DataOffsetDiscrepancyError, MultipleDataSetsError

try:
    # noinspection PyUnresolvedReferences, PyUnboundLocalVariable
    basestring
except NameError:
    # noinspection PyShadowingBuiltins
    basestring = str


def _next_power_of_2(x):
    if x == 0:
        return 1
    else:
        return 2 ** (x - 1).bit_length()


class FlowData(object):
    """
    Object representing a Flow Cytometry Standard (FCS) file.
    FCS versions 2.0, 3.0, and 3.1 are supported.

    Note on ignore_offset_error:
        Some FCS files incorrectly report the location of the last data byte
        as the last byte exclusive of the data section rather than the last
        byte inclusive of the data section. Technically, these are invalid
        FCS files but these are not corrupted data files. To attempt to read
        in these files, set the `ignore_offset_error` option to True.

    Note on ignore_offset_discrepancy and use_header_offset:
        The byte offset location for the DATA segment is defined in 2 places
        in an FCS file: the HEADER and the TEXT segments. By default, FlowIO
        uses the offset values found in the TEXT segment. If the HEADER values
        differ from the TEXT values, a DataOffsetDiscrepancyError will be
        raised. This option allows overriding this error to force the loading
        of the FCS file. The related `use_header_offset` can be used to
        force loading the file using the data offset locations found in the
        HEADER section rather than the TEXT section. Setting `use_header_offset`
        to True is equivalent to setting both options to True, meaning no
        error will be raised for an offset discrepancy.

    :ivar analysis: dictionary of key/value pairs from the ANALYSIS section (if present)
    :ivar channel_count: number of channels of event data
    :ivar channels: a dictionary of channel information, with key as channel number
        and value is a dictionary of the PnN and PnS text
    :ivar event_count: number of events
    :ivar events: 1-D array of event data
    :ivar file_size: file size of the imported FCS file
    :ivar header: dictionary of key/value pairs from the HEADER section
    :ivar name: file name of the imported FCS file
    :ivar text: dictionary of key/value pairs from the TEXT section

    :param filename_or_handle: a path string or a file handle for an FCS file
    :param ignore_offset_error: option to ignore data offset error (see above note), default is False
    :param ignore_offset_discrepancy: option to ignore discrepancy between the HEADER
        and TEXT values for the DATA byte offset location, default is False
    :param use_header_offsets: use the HEADER section for the data offset locations, default is False.
        Setting this option to True also suppresses an error in cases of an offset discrepancy.
    :param only_text: option to only read the "text" segment of the FCS file without loading event data,
        default is False
    :param nextdata_offset: an integer indicating the byte offset for a data set, used for reading
        a data set from FCS file contain multiple data sets
    """
    def __init__(
            self,
            filename_or_handle,
            ignore_offset_error=False,
            ignore_offset_discrepancy=False,
            use_header_offsets=False,
            only_text=False,
            nextdata_offset=None,
            null_channel_list=None
    ):
        # Determine input type and its name.
        # Some file handles may not have a file name, they
        # are "in memory" files.
        self.name = None
        if isinstance(filename_or_handle, str):
            # Received a string for the file path, and the name
            # attribute from the resulting file handle is a full
            # path, so strip out just the file name
            self._fh = open(str(filename_or_handle), 'rb')
            self.name = os.path.basename(self._fh.name)
        elif isinstance(filename_or_handle, Path):
            # Received a Path object. These are guaranteed to
            # have a 'name' attribute and that is the base name.
            self._fh = open(str(filename_or_handle), 'rb')
            self.name = filename_or_handle.name
        else:
            # Not a string or Path object, may be an object
            # from the 'io' module. If so, not all have a 'name'
            # attribute (e.g. StringIO), so may be in memory.
            self._fh = filename_or_handle

            if hasattr(filename_or_handle, 'name'):
                self.name = filename_or_handle.name
            else:
                self.name = "InMemoryFile"

        current_offset = nextdata_offset if nextdata_offset else 0

        self._ignore_offset = ignore_offset_error

        # Get actual file size for sanity check of data section
        self._fh.seek(0, os.SEEK_END)
        self.file_size = self._fh.tell()
        self._fh.seek(current_offset)  # reset to beginning before parsing

        # parse headers
        self.header = self.__parse_header(current_offset)

        # Get FCS version from the header for convenient lookup
        self.version = self.header['version']

        # parse text
        self.text = self.__parse_text(
            current_offset,
            self.header['text_start'],
            self.header['text_stop']
        )

        if int(self.text.get("nextdata", "0")) != 0 and nextdata_offset is None:
            self._fh.close()
            raise MultipleDataSetsError(
                "%s contains multiple data sets, use read_multiple_data_sets function" % self.name
            )

        self.channel_count = int(self.text['par'])
        self.event_count = int(self.text['tot'])

        # parse analysis
        try:
            # noinspection SpellCheckingInspection
            a_start = int(self.text['beginanalysis'])
        except KeyError:
            a_start = self.header['analysis_start']
        try:
            # noinspection SpellCheckingInspection
            a_stop = int(self.text['endanalysis'])
        except KeyError:
            a_stop = self.header['analysis_stop']

        self.analysis = self.__parse_analysis(current_offset, a_start, a_stop)

        # parse data
        # Note: For FCS 3.0 & 3.1 files, byte offset locations can be found in both
        #    the HEADER & TEXT segments. FCS 2.0 files only specify the HEADER for
        #    storing offset locations, however these files will sometimes contain
        #    TEXT keywords for the locations as well.
        #
        #    For 2.0 files we will check only the HEADER for the values.
        #    For 3.0 & 3.1 We will check both & ensure they agree. If a discrepancy
        #    is found, raise a DataOffsetDiscrepancyError. This behaviour can be
        #    overridden by setting the ignore_offset_discrepancy option to True.
        #    Users can force the use of the HEADER values for the data lookup by
        #    setting the use_header_offsets option to True.
        fcs_version = self.header['version']

        # check if FCS version is supported (3.0, 3.1)
        # If unsupported version, issue warning & try to parse like 3.1

        header_data_start = self.header['data_start']
        header_data_stop = self.header['data_stop']

        if fcs_version == '2.0':
            # FCS 2.0 didn't have offset keywords in TEXT.
            # Also, if the user specifies we'll use the HEADER.
            data_start = header_data_start
            data_stop = header_data_stop
        else:
            # For 3.0, 3.1, or some other value, check if user specified,
            # else use the TEXT section (but we'll check for discrepancy

            if use_header_offsets:
                # this option bypasses discrepancy checking between HEADER & TEXT values
                data_start = header_data_start
                data_stop = header_data_stop
            else:
                # use TEXT section
                # noinspection SpellCheckingInspection
                data_start = int(self.text['begindata'])
                # noinspection SpellCheckingInspection
                data_stop = int(self.text['enddata'])

                # check if different from HEADER values & not due to large file
                if data_start != header_data_start:
                    # may be due to large file (>99,999,999) where HEADER values will be 0
                    # The FCS 3.1 spec states:
                    #   When any portion of a segment falls outside the 99,999,999 byte
                    #   limit, '0's are substituted in the HEADER for that segments begin
                    #   and end byte offset.
                    # So we need to check the TEXT value for the DATA end location, since
                    # the limit may not be reached at the start location. If the DATA end
                    # offset is above the limit, BOTH the HEADER values should be 0.
                    if header_data_start == 0 and data_stop > 99_999_999:
                        # this is OK, it's just a large file
                        pass
                    elif ignore_offset_discrepancy:
                        # user has specified to ignore the discrepancy
                        pass
                    else:
                        self._fh.close()
                        raise DataOffsetDiscrepancyError(
                            "%s has a discrepancy in the DATA start byte location: %d (HEADER) vs %d (TEXT)"
                            % (self.name, header_data_start, data_start)
                        )

                # same logic for DATA stop location
                if data_stop != header_data_stop:
                    if header_data_stop == 0 and data_stop > 99_999_999:
                        # this is OK, it's just a large file
                        pass
                    elif ignore_offset_discrepancy:
                        # user has specified to ignore the discrepancy
                        pass
                    else:
                        self._fh.close()
                        raise DataOffsetDiscrepancyError(
                            "%s has a discrepancy in the DATA end byte location: %d (HEADER) vs %d (TEXT)"
                            % (self.name, header_data_stop, data_stop)
                        )

        if data_stop > self.file_size:
            self._fh.close()
            raise FCSParsingError("FCS file indicates data section greater than file size")

        # Extract channel metadata from the text data.
        # Need this for pre-processing the event data.
        self.channels = self.__extract_channel_metadata()

        # Setup variables we'll need for storing various channel related metadata
        self.pnn_labels = list()
        self.pns_labels = list()
        self.pnr_values = list()
        self.fluoro_indices = list()
        self.scatter_indices = list()
        self.time_index = None

        # Ensure null channels is a list for checking later
        if null_channel_list is None:
            self.null_channels = []
        else:
            self.null_channels = null_channel_list

        for n in sorted([int(k) for k in self.channels.keys()]):
            channel_dict = self.channels[n]

            channel_label = channel_dict['PnN']
            self.pnn_labels.append(channel_label)
            self.pns_labels.append(channel_dict['PnS'])
            self.pnr_values.append(channel_dict['PnR'])

            # Determine fluoro vs scatter vs time channels
            # Null channels are excluded from any category.
            # NOTE: We save the indices here, not the channel numbers.
            if channel_label in self.null_channels:
                pass
            elif channel_label.lower()[:4] not in ['fsc-', 'ssc-', 'time']:
                self.fluoro_indices.append(n - 1)
            elif channel_label.lower()[:4] in ['fsc-', 'ssc-']:
                self.scatter_indices.append(n - 1)
            elif channel_label.lower() == 'time':
                self.time_index = n - 1

                # Note: The time channel is scaled by the timestep (if present),
                # but should not be scaled by any gain value present in PnG.
                # It seems common for cytometers to include a gain value for the
                # time channel that matches either the fluoro channels or the
                # timestep keyword value. Not sure why they do this, but it
                # makes no sense to have an amplifier gain on the time data.
                # Here, we set any time gain to 1.0.
                channel_dict['PnG'] = 1.0

        if only_text:
            self.events = None
        else:
            # Parse DATA segment (returns a flat list of event data)
            self.events = self.__parse_data(
                current_offset,
                data_start,
                data_stop,
                self.text
            )

        self._fh.close()

    def __repr__(self):
        if hasattr(self, 'name'):
            name = self.name
        else:
            name = "Unread FCS data"

        return '%s(%s)' % (self.__class__.__name__, name)

    def __read_bytes(self, offset, start, stop):
        """Read in bytes from start to stop inclusive."""
        self._fh.seek(offset + start)

        data = self._fh.read(stop - start + 1)

        return data

    def __parse_header(self, offset):
        """
        Parse the FlowData FCS file at the offset (supporting multiple
        data segments in a file
        """
        header = dict()
        header['version'] = self.__read_bytes(offset, 3, 5).decode()
        header['text_start'] = int(self.__read_bytes(offset, 10, 17))
        header['text_stop'] = int(self.__read_bytes(offset, 18, 25))
        header['data_start'] = int(self.__read_bytes(offset, 26, 33))
        header['data_stop'] = int(self.__read_bytes(offset, 34, 41))
        try:
            header['analysis_start'] = int(self.__read_bytes(offset, 42, 49))
        except ValueError:
            header['analysis_start'] = -1
        try:
            header['analysis_stop'] = int(self.__read_bytes(offset, 50, 57))
        except ValueError:
            header['analysis_stop'] = -1

        return header

    def __parse_text(self, offset, start, stop):
        """return parsed text segment of FCS file"""
        num_items = (stop - start + 1)
        self._fh.seek(offset + start)
        tmp = array.array('b')
        tmp.fromfile(self._fh, int(num_items))
        tmp = tmp.tobytes()

        try:
            # try UTF-8 first
            tmp = tmp.decode()
        except UnicodeDecodeError:
            # next best guess is Latin-1, if not that either, we throw the exception
            tmp = tmp.decode("ISO-8859-1")
        return self.__parse_pairs(tmp)

    def __parse_analysis(self, offset, start, stop):
        """return parsed analysis segment of FCS file"""
        if start == stop:
            return {}
        else:
            # FCS standard states:
            #    The ANALYSIS segment has the same structure as the TEXT
            #    segment; i.e., it consists of a series of keyword-value
            #    pairs. There are no required keywords for the ANALYSIS
            #    segment.
            # So we'll use the __parse_text method to parse this section.
            return self.__parse_text(offset, start, stop)

    def __parse_data(self, offset, start, stop, text):
        """
        Return array of data segment of FCS file
        """
        data_type = text['datatype']
        mode = text['mode']

        # FlowData only supports list mode data ('l')
        # Values 'c' & 'u' are deprecated in FCS 3.1 and
        # correspond to correlated multivariate histogram ('c')
        # and uncorrelated univariate histogram ('u') data.
        if mode == 'c' or mode == 'u':
            self._fh.close()
            raise NotImplementedError(
                "FCS data stored as type \'%s\' is unsupported" % mode
            )

        # noinspection SpellCheckingInspection
        if text['byteord'] == '1,2,3,4' or text['byteord'] == '1,2':
            order = '<'
        elif text['byteord'] == '4,3,2,1' or text['byteord'] == '2,1':
            order = '>'
        else:
            # noinspection SpellCheckingInspection
            warn("unsupported byte order %s , using default @" % text['byteord'])
            order = '@'
            # from here on out we assume mode "l" (list)

        if data_type.lower() == 'i':
            # For int data we need to check the bit width and range values.
            # The PnR value specifies the max value for the channel. This
            # value is exclusive, e.g. a value of 1024 means the highest
            # integer value allowed is 1023. Integer data needs to be
            # bit-masked according to this max range value.
            bit_width_by_channel = {}
            max_range_by_channel = {}
            for i in range(1, int(text['par']) + 1):
                bit_width_by_channel[i] = int(text['p%db' % i])

                # Need to verify the value is a power of 2
                tmp_max_range = int(text['p%dr' % i])
                max_range_by_channel[i] = _next_power_of_2(tmp_max_range)

            data = self.__parse_int_data(
                offset,
                start,
                stop,
                bit_width_by_channel,
                max_range_by_channel,
                order
            )
        else:
            data = self.__parse_non_int_data(
                offset,
                start,
                stop,
                data_type.lower(),
                order
            )

        return data

    def __calc_data_item_count(self, start, stop, data_type_size):
        # calculate how much data to read in.
        data_sect_size = stop - start + 1
        data_mod = data_sect_size % data_type_size

        if data_mod > 0:
            # Some FCS files incorrectly report the location of the last data byte
            # as the last byte exclusive of the data section rather than the last
            # byte inclusive of the data section. This means the stop location will
            # be off by +1. Technically, this is an invalid FCS file, but since
            # it is so common, we will try to parse these files. For any discrepancy
            # other than +1 we throw an error
            if data_mod == 1 and self._ignore_offset:
                # warn user that the offset is off
                warn_msg = "FCS file %s reported incorrect data offset. " % self.name
                warn_msg += "Attempting to parse data section, but event data should be "
                warn_msg += "reviewed before trusting this file."
                warn(warn_msg)

                stop = stop - 1
                data_sect_size = data_sect_size - 1
            elif data_mod == 1 and not self._ignore_offset:
                # attempt to close file handle before raising error
                self._fh.close()

                err_msg = "FCS file %s reports a data offset that is off by 1. " % self.name
                err_msg += "Set `ignore_offset_error=True` to force reading in this file."
                raise FCSParsingError(err_msg)
            else:
                # attempt to close file handle before raising error
                self._fh.close()

                raise FCSParsingError("Unable to determine the correct byte offsets for event data")

        num_items = data_sect_size / data_type_size

        return num_items, stop

    def __parse_int_data(
            self,
            offset,
            start,
            stop,
            bit_width_lut,
            max_range_lut,
            order
    ):
        """Parse out and return integer list data from FCS file"""

        if reduce(and_, [item in [8, 16, 32] for item in bit_width_lut.values()]):
            # Determine if we have uniform bit width values for all parameters.
            # If so, use array.array for much faster parsing
            if len(set(bit_width_lut.values())) == 1:
                # We do have a uniform bit width, grab the 1st value to
                # determine the number of actual events
                bit_width = list(bit_width_lut.values())[0]
                data_type_size = bit_width / 8
                num_items, stop = self.__calc_data_item_count(start, stop, data_type_size)

                # Here, we're reading the initial data array, but some channel
                # data may still need bit-masking correction using max range
                self._fh.seek(offset + start)
                tmp = array.array(self.__format_integer(bit_width))
                tmp.fromfile(self._fh, int(num_items))
                if order == '>':
                    tmp.byteswap()

                # If any bits higher shall be
                # ignored using a bit mask. If the PnR value is not a power
                # of 2, then the next power of 2 shall be used.
                if any(2 ** bit_width_lut[c] > max_range_lut[c] for
                       c in bit_width_lut.keys()):

                    amount_data_points = int(num_items / len(max_range_lut))
                    
                    # Create bit mask array matching length of our data array,
                    # with values for every position being the max range value.
                    bit_mask = array.array(
                        self.__format_integer(bit_width),
                        [mr - 1 for mr in max_range_lut.values()] * amount_data_points
                    )
                    new_tmp = array.array(self.__format_integer(bit_width))
                    new_tmp.frombytes(bytes(map(lambda a, b: a & b, tmp.tobytes(), bit_mask.tobytes())))
                    tmp = new_tmp
            else:
                # parameter sizes are different
                # e.g. 8, 8, 16, 8, 32 ...
                # can't use array for heterogeneous bit widths
                # TODO: Now that we have NumPy as a dependency, investigate whether
                #       using NumPy arrays can speed this up.
                tmp = self.__extract_var_length_int(
                    bit_width_lut,
                    max_range_lut,
                    offset,
                    order,
                    start,
                    stop
                )

        else:  # non-standard bit width...  Does this happen?
            warn('Non-standard bit width for data segments')
            return None

        return tmp

    def __extract_var_length_int(self, bit_width_by_channel, max_range_by_channel, 
                                 offset, order, start, stop):
        data_format = order
        for cur_width in bit_width_by_channel.values():
            data_format += '%s' % self.__format_integer(cur_width)

        # array module doesn't have a function to heterogeneous bit widths,
        # so fall back to the slower unpack approach
        tuple_tmp = iter_unpack(data_format, self.__read_bytes(offset, start, stop))
        if any(2**bit_width_by_channel[c] > max_range_by_channel[c] for 
               c in bit_width_by_channel.keys()):
            tmp = []
            for data_tuple in tuple_tmp:
                for channel, max_range in max_range_by_channel.items():
                    tmp.append(data_tuple[channel-1] % max_range)
        else:
            tmp = [ti for t in tuple_tmp for ti in t]
        
        return tmp

    def __parse_non_int_data(self, offset, start, stop, data_type, order):
        """Parse out and return float or ASCII list data from FCS file"""
        data_type_size = calcsize(data_type)
        num_items, stop = self.__calc_data_item_count(start, stop, data_type_size)

        self._fh.seek(offset + start)
        tmp = array.array(data_type)
        tmp.fromfile(self._fh, int(num_items))
        if order == '>':
            tmp.byteswap()
        return tmp

    @staticmethod
    def __parse_pairs(text):
        """return key/value pairs from a delimited string"""
        delimiter = text[0]

        if delimiter == r'|':
            delimiter = r'\|'
        elif delimiter == r'\a'[0]:  # test for delimiter being \
            delimiter = '\\\\'  # regex will require it to be \\
        elif delimiter == r'*':
            delimiter = r'\*'

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
            raise FCSParsingError(
                "Invalid integer bit size (%d) for event data. Compatible sizes are 8, 16, & 32." % b
            )

    def __extract_channel_metadata(self):
        """
        Returns a dictionary of channels, with key as channel number
        and value is a dictionary of the PnN and PnS text
        """
        channels = dict()

        # Find the required PnN values in the metadata so we know how many channels
        # there are in the FCS file.
        regex_pnn = re.compile(r"^p(\d+)n$", re.IGNORECASE)

        # Search through all metadata keys once to find the PnN values
        for i in self.text.keys():
            match = regex_pnn.match(i)
            if not match:
                continue

            channel_num = int(match.groups()[0])
            channels[channel_num] = dict()

            channels[channel_num]['PnN'] = self.text[match.group()]


        # Now iterate through the known channels to find the fields:
        #     PnE: amplification type for log/lin scale (required)
        #     PnG: channel gain (optional)
        #     PnR: maximum data range (required)
        #     PnS: alternate channel labels (optional)
        for chan_num, chan_dict in channels.items():
            # PnS is optional
            if 'p%ds' % chan_num in self.text:
                chan_dict['PnS'] = self.text['p%ds' % chan_num]
            else:
                # empty string if not present
                chan_dict['PnS'] = ''

            # PnE specifies whether the parameter data is stored in on linear or log scale
            # and includes 2 values: (f1, f2)
            # where:
            #     f1 is the number of log decades (valid values are f1 >= 0)
            #     f2 is the value to use for log(0) (valid values are f2 >= 0)
            # Note for log scale, both values must be > 0
            # linear = (0, 0)
            # log    = (f1 > 0, f2 > 0)
            if 'p%de' % chan_num in self.text:
                (decades, log0) = [
                    float(x) for x in self.text['p%de' % chan_num].split(',')
                ]
                if log0 == 0 and decades != 0:
                    log0 = 1.0  # FCS std states to use 1.0 for invalid 0 value

                chan_dict['PnE'] = (decades, log0)
            else:
                # PnE is required so should be there, but if not
                # set to linear
                chan_dict['PnE'] = (0.0, 0.0)

            # PnG is optional, value is a float
            if 'p%dg' % chan_num in self.text:
                chan_dict['PnG'] = float(self.text['p%dg' % chan_num])
            else:
                # assumed 1.0 if absent
                chan_dict['PnG'] = 1.0

            # PnR is required
            chan_dict['PnR'] = float(self.text['p%dr' % chan_num])

        return channels

    def as_array(self, preprocess=True):
        """
        Retrieve the event data list as a 2-D NumPy array. Pre-processing is
        applied if requested and includes applying gain, log, and time scaling
        as necessary.

        :param preprocess: Boolean for whether to apply gain, log, and  time
            scaling as necessary according the FCS metadata (default is True).

        :return: NumPy array of 2-D event data
        """
        # Start processing the event data. Ensure events are double precision
        # because pre-processing will convert all events (even integer data types)
        # to floating point. This precision is needed for accurate downstream
        # analysis (e.g. gating results).
        tmp_events = np.reshape(
            np.array(self.events, dtype=np.float64),
            (-1, self.channel_count)
        )

        if preprocess:
            # Event data must be scaled according to channel gain, as well
            # as corrected for proper lin/log display, and the time channel
            # scaled by the 'timestep' keyword value (if present).
            # We'll start with the time channel.
            if 'timestep' in self.text and self.time_index is not None:
                try:
                    time_step = float(self.text['timestep'])
                except ValueError:
                    if self.text['timestep'] == ' ':
                        time_step = 1.0
                    else:
                        raise ValueError(f"Timestep value should be a float value but found the value '{self.text['timestep']}'")
                tmp_events[:, self.time_index] = tmp_events[:, self.time_index] * time_step

            # Process channels
            # For channel data stored on logarithmic scale will get converted
            # to a linear scale. For channel's stored with amplified data, where
            # gain (PnG) is != 1.0 (or zero, since it's equivalent to no gain).
            for chan_num, chan_dict in self.channels.items():
                # Note that keys are channel numbers, not indices
                chan_idx = chan_num - 1
                (chan_decades, chan_log0) = chan_dict['PnE']
                chan_range = chan_dict['PnR']
                chan_gain = chan_dict['PnG']

                if chan_decades > 0:
                    tmp_events[:, chan_idx] = (10 ** (chan_decades * tmp_events[:, chan_idx] / chan_range)) * chan_log0

                if chan_gain != 1.0 and chan_gain != 0:
                    tmp_events[:, chan_idx] = tmp_events[:, chan_idx] / chan_gain

        return tmp_events

    def write_fcs(self, filename, metadata=None):
        """
        Export FlowData instance as a new FCS file.

        By default, the output FCS file will include the $cyt, $date, and $spill
        keywords (and values) from the FlowData instance. To exclude these keys,
        specify a custom `metadata` dictionary (including an empty dictionary for
        the bare minimum metadata). Note: Any critical keywords related to the
        interpretation of the event data are defined and set internally,
        overriding those in the provided `metadata` dictionary. These keywords
        include: PnB, PnE, and PnG.

        :param filename: name of exported FCS file
        :param metadata: an optional dictionary for adding metadata keywords/values
        :return: None
        """
        if self.events is None:
            raise AttributeError(
                "FlowData instance does not contain event data. This might"
                "occur if the FCS file was read with the only_text=True option."
            )

        if metadata is None:
            metadata = {}

            # by default, we'll add the $cyt, $date, & $spillover (or $spill) metadata
            if 'spillover' in self.text:
                metadata['spillover'] = self.text['spillover']
            elif 'spill' in self.text:
                metadata['spillover'] = self.text['spill']

            if 'date' in self.text:
                metadata['date'] = self.text['date']

            if 'cyt' in self.text:
                metadata['cyt'] = self.text['cyt']

            # TODO: we need to verify if other PnX sets
            #  need to be included (esp. PnG) since this
            #  method will write out the unprocessed events,
            #  these values may need to be preserved.

            # copy PnR values from file
            for i, value in enumerate(self.pnr_values):
                # Use channel numbers and not indices
                chan_num = i + 1
                metadata['P%dR' % chan_num] = str(value)

        fh = open(filename, 'wb')
        fh = create_fcs(
            fh,
            self.events,
            self.pnn_labels,
            opt_channel_names=self.pns_labels,
            metadata_dict=metadata
        )
        fh.close()
