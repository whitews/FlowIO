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
    spill is optional text value that should conform to version 3.1 of the
    FCS Standard 3.1. A proper spillover matrix shall have the first value
    corresponding to the number of compensated fluorescence channels followed
    by the $PnN names which should match the given channel_names argument. All
    values in the spill text string should be comma delimited with no newline
    characters.

    cyt is an optional text string to use for the $CYT field

    extra is an option dictionary for adding extra non-standard keywords/values

    :param event_data:
    :param channel_names:
    :param file_handle:
    :param spill:
    :param cyt:
    :param date:
    :param extra:
    :param extra_non_standard:
    :param opt_channel_names:

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
    # ENDDATA. Our data begins at the:
    #  initial location + (string length of the initial location plus 2)
    text_string = build_text(
        text,
        delimiter,
        extra_dict=extra,
        extra_dict_non_standard=extra_non_standard
    )
    initial_offset = text_start + len(text_string)
    final_start_data_offset = initial_offset + len(str(initial_offset + 2))
    # and tack on the ENDDATA string length
    final_start_data_offset += len(str(final_start_data_offset + data_size))
    text['BEGINDATA'] = str(final_start_data_offset)
    text['ENDDATA'] = str(final_start_data_offset + data_size - 1)

    # re-build text section and sanity check the data start location
    text_string = build_text(
        text,
        delimiter,
        extra_dict=extra,
        extra_dict_non_standard=extra_non_standard
    )
    if text_start + len(text_string) != int(text['BEGINDATA']):
        raise Exception("something went wrong calculating the offsets")

    #
    # Start writing to file, beginning with header
    #
    file_handle.seek(0)
    file_handle.write('FCS3.1'.encode())
    spaces = ' ' * 4
    file_handle.write(spaces.encode())  # spaces for bytes 6 -> 9
    file_handle.write('{0: >8}'.format(str(text_start)).encode())

    # Text end byte is one less than where our data starts
    file_handle.write('{0: >8}'.format(str(final_start_data_offset - 1)).encode())

    # TODO: set zeroes if data offsets are greater than header max data size

    # data start byte location
    file_handle.write('{0: >8}'.format(text['BEGINDATA']).encode())

    # data end byte location
    file_handle.write('{0: >8}'.format(text['ENDDATA']).encode())

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
