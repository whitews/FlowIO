from .flowdata import FlowData
from .exceptions import MultipleDataSetsError

def read_multiple_data_sets(
    filename_or_handle,
    ignore_offset_error=False,
    ignore_offset_discrepancy=False,
    use_header_offsets=False,
    only_text=False
):
    """
    Utility function for reading all data sets contained in an FCS file.

    :param filename_or_handle: a path string or a file handle for an FCS file
    :param ignore_offset_error: option to ignore data offset error (see above note), default is False
    :param ignore_offset_discrepancy: option to ignore discrepancy between the HEADER
        and TEXT values for the DATA byte offset location, default is False
    :param use_header_offsets: use the HEADER section for the data offset locations, default is False.
        Setting this option to True also suppresses an error in cases of an offset discrepancy.
    :param only_text: option to only read the "text" segment of the FCS file without loading event data,
        default is False

    :return: List of FlowData instances for each found data set
    """
    data_sets = []
    nextdata_offset = 0

    # Multi-data set FCS files contain a 'nextdata' keyword with the byte
    # offset to the next data set. Note, the 3.1 spec deprecates this
    # feature but also isn't clear on the byte offset meaning. The 2.0
    # spec does specify that the offset is relative to the first byte
    # of the current data set...so not absolute byte locations. Finally,
    # a 'nextdata' value of zero indicates the last data set.
    #
    # We'll loop through til we find a zero 'nextdata' value. However, it is
    # possible that a maliciously crafted FCS file could cause an infinite
    # loop, i.e. data set B refers to data set C which refers back to data
    # set B. The 'nextdata' values are supposed to be positive integers, but
    # there is nothing preventing the presence of negative values that could
    # have us jump to a previous location.
    # To avoid this, we'll store the offset locations we
    # encounter in a set and end if a repeat is encountered. In the case where
    # erroneous offsets are provided the FlowData constructor will fail and
    # end the loop.
    while True:
        fd = FlowData(
            filename_or_handle,
            ignore_offset_error=ignore_offset_error,
            ignore_offset_discrepancy=ignore_offset_discrepancy,
            use_header_offsets=use_header_offsets,
            only_text=only_text,
            nextdata_offset=nextdata_offset
        )
        data_sets.append(fd)
        next_data = int(fd.text["nextdata"])

        if next_data == 0:
            return data_sets
        elif next_data < 0:
            # suspicious negative byte offset
            raise MultipleDataSetsError("Input file contains invalid negative byte offset to next data set")

        # At this point, next_data is > 0, increasing our offset
        # and guaranteeing the loop ends by reaching EoF
        nextdata_offset += next_data
