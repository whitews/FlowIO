from array import array
from collections import OrderedDict


def create_fcs(
        event_data,
        channel_names,
        file_handle,
        spill=None,
        cyt=None,
        date=None,
        extra=None,
        extra_non_standard=None,
        opt_channel_names=None):
    """
    Create a new FCS file from a list of event data.

    Note:
        A proper spillover matrix shall have the first value corresponding to the
        number of compensated fluorescence channels followed by the $PnN names
        which should match the given channel_names argument. All values in the
        spill text string should be comma delimited with no newline characters.

    :param event_data: list of event data (flattened 1-D list)
    :param channel_names: list of channel labels to use for PnN fields
    :param file_handle: file handle for new FCS file
    :param spill: optional text for spillover matrix conforming to FCS 3.1 specification
    :param cyt: optional text string to use for the $CYT field
    :param date: optional text string to use for the $DATE field
    :param extra: an optional dictionary for adding extra standard keywords/values
    :param extra_non_standard: an optional dictionary for adding extra non-standard keywords/values
    :param opt_channel_names: optional list of channel labels to use for PnS fields

    :return:
    """
    def build_text(
            text_dict,
            text_delimiter,
            extra_dict=None,
            extra_dict_non_standard=None
    ):
        result = text_delimiter

        # iterate through all the key/value pairs, checking for the presence
        # of the delimiter in any value. If present, double the delimiter per
        # the FCS specification, as values are not allowed to be zero-length,
        # this is how the delimiter can be included in a keyword value.

        for key in text_dict.keys():
            result += '$%s%s%s%s' % (
                key,
                text_delimiter,
                text_dict[key].replace(text_delimiter, text_delimiter * 2),
                text_delimiter
            )

        if extra_dict is not None:
            for key in extra_dict.keys():
                result += '$%s%s%s%s' % (
                    key,
                    text_delimiter,
                    extra_dict[key].replace(text_delimiter, text_delimiter * 2),
                    text_delimiter
                )

        if extra_dict_non_standard is not None:
            for key in extra_dict_non_standard.keys():
                result += '%s%s%s%s' % (
                    key,
                    text_delimiter,
                    extra_dict_non_standard[key].replace(
                        text_delimiter, text_delimiter * 2
                    ),
                    text_delimiter
                )

        return result

    text_start = 256  # arbitrarily start at byte 256.
    delimiter = '/'  # use / as our delimiter.

    # Collect some info from the user specified inputs
    # and do some sanity checking
    n_channels = len(channel_names)
    if opt_channel_names is not None:
        n_opt_channels = len(opt_channel_names)
        if n_opt_channels != n_channels:
            raise ValueError(
                "Number of PnN labels does not match the number of PnS channels"
            )

    n_points = len(event_data)

    if n_points == 0:
        raise ValueError(
            "'event_data' array provided was empty"
        )

    if not n_points % n_channels == 0:
        raise ValueError(
            "Number of data points is not a multiple of the number of channels"
        )
    data_size = 4 * n_points  # 4 bytes per float (we only store floats)

    # Construct the primary text section using OrderedDict to preserve order
    text = OrderedDict()
    text['BEGINANALYSIS'] = '0'
    text['BEGINDATA'] = ''  # IMPORTANT: this gets replaced later
    text['BEGINSTEXT'] = '0'
    text['BYTEORD'] = '1,2,3,4'  # little endian
    text['DATATYPE'] = 'F'  # only do float data
    text['ENDANALYSIS'] = '0'
    text['ENDDATA'] = ''  # IMPORTANT: this gets replaced as well
    text['ENDSTEXT'] = '0'
    text['MODE'] = 'L'  # only do list mode data
    text['NEXTDATA'] = '0'
    text['PAR'] = str(n_channels)
    text['TOT'] = str(int(n_points / n_channels))

    if spill is not None:
        text['SPILLOVER'] = spill

    if cyt is not None:
        text['CYT'] = cyt

    if date is not None:
        text['DATE'] = date

    # calculate the max value, which we'll use for the $PnR field for all
    # channels. We'll use a magic number of 262144 if the true max value is
    # below that value, or the actual max value if above. 262144 (2^18) is
    # used by many cytometers and by FlowJo to determine the default display
    # range for plotting.
    if max(event_data) < 262144:
        pnr_value = '262144'
    else:
        pnr_value = str(max(event_data))

    for i in range(n_channels):
        text['P%dB' % (i + 1)] = '32'  # float requires 32 bits
        text['P%dE' % (i + 1)] = '0,0'
        text['P%dR' % (i + 1)] = pnr_value
        text['P%dN' % (i + 1)] = channel_names[i]

        if opt_channel_names is not None:
            # cannot have zero-length values in FCS keyword values
            if opt_channel_names[i] not in [None, '']:
                text['P%dS' % (i + 1)] = opt_channel_names[i]

    # Calculate initial text size, but it's tricky b/c the text contains the
    # byte offset location for the data, which depends on the size of the
    # text section. We set placeholder empty string values for BEGINDATA &
    # ENDDATA. We know both of these will not be zero-length strings in the
    # end. Our data begins at the:
    #  initial location + (string length of the initial location plus 2)
    text_string = build_text(
        text,
        delimiter,
        extra_dict=extra,
        extra_dict_non_standard=extra_non_standard
    )
    # initial offset is the minimum offset the data can start IF the
    # BEGINDATA & ENDDATA text values were allowed to be empty strings
    # NOTE: end data value is the location of the last data byte (so minus 1)
    initial_begin_data_offset = text_start + len(text_string)
    initial_end_data_offset = initial_begin_data_offset + data_size - 1

    # data start offset location must account for the string lengths
    # of BOTH the BEGINDATA & ENDDATA text values.
    # get initial BEGINDATA string length
    begin_data_value_length = len(str(initial_begin_data_offset))
    # get initial ENDDATA string length
    end_data_value_length = len(str(initial_end_data_offset))

    # now determine how close either of these are to adding a new digit
    begin_data_mod = 10**begin_data_value_length % initial_begin_data_offset
    end_data_mod = 10**end_data_value_length % initial_end_data_offset

    # since neither our initial offsets include the value lengths,
    # if a mod value <= the sum of the value lengths AND not zero,
    # then the BEGINDATA offset needs to be incremented by 1.
    # If both mod values are <= sum of value lengths, then the
    # BEGINDATA offset needs to be incremented by 2.
    #
    # Note if a mod value is 0 then the offset just ticked over
    # to a new digit length (e.g. 1000) and is in no danger of
    # increasing another digit
    total_data_values_length = begin_data_value_length + end_data_value_length
    begin_data_offset_correction = 0
    if begin_data_mod <= total_data_values_length and begin_data_mod != 0:
        begin_data_offset_correction += 1
    if end_data_mod <= total_data_values_length and end_data_mod != 0:
        begin_data_offset_correction += 1

    final_begin_data_offset = initial_begin_data_offset + \
        begin_data_value_length + \
        end_data_value_length + \
        begin_data_offset_correction

    text['BEGINDATA'] = str(final_begin_data_offset)
    text['ENDDATA'] = str(final_begin_data_offset + data_size - 1)

    # re-build text section and sanity check the data start location
    text_string = build_text(
        text,
        delimiter,
        extra_dict=extra,
        extra_dict_non_standard=extra_non_standard
    )
    # verify the final BEGINDATA value == text start position + length of the text string
    if text_start + len(text_string) != int(text['BEGINDATA']):
        raise Exception("REPORT BUG: error calculating text offset")

    #
    # Start writing to file, beginning with header
    #
    file_handle.seek(0)
    file_handle.write('FCS3.1'.encode())
    spaces = ' ' * 4
    file_handle.write(spaces.encode())  # spaces for bytes 6 -> 9
    file_handle.write('{0: >8}'.format(str(text_start)).encode())

    # Text end byte is one less than where our data starts
    file_handle.write('{0: >8}'.format(str(final_begin_data_offset - 1)).encode())

    # Header contains data start and end byte locations. However,
    # the FCS 3.1 spec allows for only 8-byte ASCII encoded integers.
    # So, each value is limited to 99,999,999. If data section extends
    # past 99,999,999 bytes then both the data start & end values shall
    # be set to zero.
    byte_limit = 99999999
    if int(text['ENDDATA']) <= byte_limit:
        file_handle.write('{0: >8}'.format(text['BEGINDATA']).encode())
        file_handle.write('{0: >8}'.format(text['ENDDATA']).encode())
    else:
        file_handle.write('{0: >8}'.format('0').encode())
        file_handle.write('{0: >8}'.format('0').encode())

    # We don't support analysis sections so write space padded 8 byte '0'
    file_handle.write('{0: >8}'.format('0').encode())

    # Ditto for the analysis end
    file_handle.write('{0: >8}'.format('0').encode())

    # Write spaces until the start of the text segment
    spaces = ' ' * (text_start - file_handle.tell())
    file_handle.write(spaces.encode())

    # Write out the entire text section
    file_handle.write(text_string.encode())

    # And now our data!
    float_array = array('f', event_data)
    float_array.tofile(file_handle)

    return file_handle
