def create_fcs(events, channel_names, filename, extra=None):

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

    ## Write TEXT Segment
    text_start = 256  # arbitrarily start at byte 256.
    delimiter = '/'  # use / as our delimiter.

    # Write spaces until the start of the txt segment
    fh.seek(58)
    fh.write(' ' * (text_start - fh.tell()))

    n_channels = len(channel_names)
    n_points = len(events)
    data_size = 4 * n_points  # 4 bytes to hold float

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
    text['TOT'] = str(n_points / n_channels)
    for i in range(n_channels):
        text['P%dB' % (i + 1)] = '32'  # float requires 32 bits
        text['P%dE' % (i + 1)] = '0,0'
        text['P%dR' % (i + 1)] = str(max(events))
        text['P%dN' % (i + 1)] = channel_names[i]
        text['P%dS' % (i + 1)] = channel_names[i]

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
    fh.write(str(float(i) for i in events))

    fh.seek(header_text_start[0])
    fh.write(str(text_start))
    fh.seek(header_text_end[0])
    fh.write(str(text_end))

    fh.seek(header_data_start[0])
    if len(str(data_end)) <= (header_data_end[1] - header_data_end[0] + 1):
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