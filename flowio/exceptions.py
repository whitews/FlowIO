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