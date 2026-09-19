"""
flowio.exceptions
~~~~~~~~~~~~~~~~~
This module contains custom FlowIO exception and warning classes.
"""


class FlowIOWarning(Warning):
    """Generic FlowIO warning"""
    pass


class PnEWarning(FlowIOWarning):
    """Warning for invalid PnE values when creating FCS files"""
    pass


class FlowIOException(Exception):
    """Generic FlowIO exception"""
    pass


class FCSParsingError(FlowIOException):
    """Errors relating to parsing an FCS file"""


class DataOffsetDiscrepancyError(FCSParsingError):
    """
    Raised when an FCS file's HEADER & TEXT section provide different byte
    offsets for the DATA section.
    """
    pass


class MultipleDataSetsError(FlowIOException):
    """
    Raised for errors related to FCS files containing more than one dataset, indicated by
    the 'nextdata' keyword.
    """
    pass


class UnsupportedLazyDataError(FlowIOException):
    """
    Raised when lazy or memory-mapped DATA access is not supported for an FCS layout
    (for example ASCII datatype, variable channel bit widths, or a non-path file handle
    when event data was not loaded).
    """
    pass
