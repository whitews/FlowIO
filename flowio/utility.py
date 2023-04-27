from .flowdata import FlowData

def read_multiple_flowframes(filename_or_handle,
                             ignore_offset_error=False,
                             ignore_offset_discrepancy=False,
                             use_header_offsets=False,
                             only_text=False,):
    """
    Utility function for reading all datasets contained in an fcs/lmd file.


    :param filename_or_handle: a path string or a file handle for an FCS file
    :param ignore_offset_error: option to ignore data offset error (see above note), default is False
    :param ignore_offset_discrepancy: option to ignore discrepancy between the HEADER
        and TEXT values for the DATA byte offset location, default is False
    :param use_header_offsets: use the HEADER section for the data offset locations, default is False.
        Setting this option to True also suppresses an error in cases of an offset discrepancy.
    :param only_text: option to only read the "text" segment of the FCS file without loading event data,
        default is False

    :return: List of FlowData instances for each found dataset
    """
    frames = []
    nextdata_offset = 0
    while True:
        frame = FlowData(filename_or_handle,
                         ignore_offset_error,
                         ignore_offset_discrepancy,
                         use_header_offsets,
                         only_text,
                         nextdata_offset=nextdata_offset)
        frames.append(frame)
        nextdata = int(frame.text["nextdata"])
        if nextdata == 0:
            return frames
        nextdata_offset += nextdata
        

     