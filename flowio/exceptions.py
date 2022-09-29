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
