import numpy as np

try:
    from . import _preprocessing_ext
except ImportError:
    _preprocessing_ext = None


HAS_PREPROCESSING_EXTENSION = _preprocessing_ext is not None


def _as_float64_channels(values, channel_count, name):
    values = np.asarray(values, dtype=np.float64)

    if values.ndim != 1:
        raise ValueError(f"{name} must be a 1-D float64 NumPy array")

    if values.shape[0] != channel_count:
        raise ValueError(
            f"{name} must contain one value per channel "
            f"({values.shape[0]} != {channel_count})"
        )

    return values


def apply_preprocessing_numpy(events, decades, log0, ranges, gains):
    """
    Apply FlowIO preprocessing using the existing NumPy implementation.

    This preserves FlowIO's fallback behavior for environments where the
    optional C extension is unavailable.
    """
    tmp_events = np.asarray(events, dtype=np.float64, order='C')

    if tmp_events.ndim != 2:
        raise ValueError("events must be a 2-D float64 NumPy array")

    channel_count = tmp_events.shape[1]
    decades = _as_float64_channels(decades, channel_count, 'decades')
    log0 = _as_float64_channels(log0, channel_count, 'log0')
    ranges = _as_float64_channels(ranges, channel_count, 'ranges')
    gains = _as_float64_channels(gains, channel_count, 'gains')

    for chan_idx in range(channel_count):
        chan_decades = decades[chan_idx]
        chan_log0 = log0[chan_idx]
        chan_range = ranges[chan_idx]
        chan_gain = gains[chan_idx]

        if chan_decades > 0:
            tmp_events[:, chan_idx] = (
                10 ** (chan_decades * tmp_events[:, chan_idx] / chan_range)
            ) * chan_log0

        if chan_gain != 1.0 and chan_gain != 0.0:
            tmp_events[:, chan_idx] = tmp_events[:, chan_idx] / chan_gain

    return tmp_events


def apply_preprocessing(events, decades, log0, ranges, gains):
    """
    Apply FlowIO preprocessing, preferring the optional C extension when
    available and otherwise falling back to the NumPy implementation.
    """
    tmp_events = np.asarray(events, dtype=np.float64, order='C')

    if tmp_events.ndim != 2:
        raise ValueError("events must be a 2-D float64 NumPy array")

    channel_count = tmp_events.shape[1]
    decades = _as_float64_channels(decades, channel_count, 'decades')
    log0 = _as_float64_channels(log0, channel_count, 'log0')
    ranges = _as_float64_channels(ranges, channel_count, 'ranges')
    gains = _as_float64_channels(gains, channel_count, 'gains')

    if HAS_PREPROCESSING_EXTENSION:
        return _preprocessing_ext.apply_preprocessing(
            tmp_events,
            decades,
            log0,
            ranges,
            gains
        )

    return apply_preprocessing_numpy(tmp_events, decades, log0, ranges, gains)
