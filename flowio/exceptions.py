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

class DataOffsetDiscrepancyError(Exception):
    """Generic FlowIO exception"""
    pass