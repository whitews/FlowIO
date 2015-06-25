from array import array
from collections import OrderedDict


def create_fcs(event_data, channel_names, file_handle, spill=None):
    """
    spill is optional text value that should conform to version 3.1 of the
    FCS Standard 3.1. A proper spillover matrix shall have the first value
    corresponding to the number of compensated fluorescence channels followed
    by the $PnN names which should match the given channel_names argument. All
    values in the spill text string should be comma delimited with no newline
    characters.
    :param event_data:
    :param channel_names:
    :param file_handle:
    :param spill:
    :return:
    """
    def build_text(text_dict, text_delimiter):
        result = text_delimiter
        for key in text_dict.keys():
            result += '$%s%s%s%s' % (
                key,
                text_delimiter,
                text_dict[key],
                text_delimiter
            )
        return result

    text_start = 256  # arbitrarily start at byte 256.
    delimiter = '/'  # use / as our delimiter.

    # Collect some info from the user specified inputs
    # and do some sanity checking
    n_channels = len(channel_names)
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
    text['TOT'] = str(n_points / n_channels)
    for i in range(n_channels):
        text['P%dB' % (i + 1)] = '32'  # float requires 32 bits
        text['P%dE' % (i + 1)] = '0,0'
        text['P%dR' % (i + 1)] = str(max(event_data))
        text['P%dN' % (i + 1)] = channel_names[i]

    if spill is not None:
        text['SPILLOVER'] = spill

    # Calculate initial text size, but it's tricky b/c the text contains the
    # byte offset location for the data, which depends on the size of the
    # text section. We set placeholder empty string values for BEGINDATA &
    # ENDDATA. Our data begins at the:
    #  initial location + (string length of the initial location plus 2)
    text_string = build_text(text, delimiter)
    initial_offset = text_start + len(text_string)
    final_start_data_offset = initial_offset + len(str(initial_offset + 2))
    # and tack on the ENDDATA string length
    final_start_data_offset += len(str(final_start_data_offset + data_size))
    text['BEGINDATA'] = str(final_start_data_offset)
    text['ENDDATA'] = str(final_start_data_offset + data_size - 1)

    # re-build text section and sanity check the data start location
    text_string = build_text(text, delimiter)
    if text_start + len(text_string) != int(text['BEGINDATA']):
        raise Exception("something went wrong calculating the offsets")

    #
    # Start writing to file, beginning with header
    #
    file_handle.seek(0)
    file_handle.write('FCS3.1')
    file_handle.write(' ' * 4)  # spaces for bytes 6 -> 9
    file_handle.write('{0: >8}'.format(str(text_start)))

    # Text end byte is one less than where our data starts
    file_handle.write('{0: >8}'.format(str(final_start_data_offset - 1)))

    # TODO: set zeroes if data offsets are greater than header max data size

    # data start byte location
    file_handle.write('{0: >8}'.format(text['BEGINDATA']))

    # data end byte location
    file_handle.write('{0: >8}'.format(text['ENDDATA']))

    # We don't support analysis sections so write space padded 8 byte '0'
    file_handle.write('{0: >8}'.format('0'))

    # Ditto for the analysis end
    file_handle.write('{0: >8}'.format('0'))

    # Write spaces until the start of the text segment
    file_handle.write(' ' * (text_start - file_handle.tell()))

    # Write out the entire text section
    file_handle.write(text_string)

    # And now our data!
    float_array = array('f', event_data)
    float_array.tofile(file_handle)

    return file_handle
