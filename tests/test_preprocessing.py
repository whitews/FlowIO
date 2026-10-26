import unittest

import numpy as np

from flowio import FlowData
from flowio._preprocessing import (
    HAS_PREPROCESSING_EXTENSION,
    apply_preprocessing_numpy
)

try:
    from flowio import _preprocessing_ext
except ImportError:
    _preprocessing_ext = None


class PreprocessingTestCase(unittest.TestCase):
    @staticmethod
    def test_numpy_fallback_applies_per_channel_metadata():
        events = np.array(
            [
                [8.0, 0.0, 2.0, 7.0],
                [10.0, 1.0, 3.0, 9.0]
            ],
            dtype=np.float64
        )
        decades = np.array([0.0, 2.0, 1.0, 0.0], dtype=np.float64)
        log0 = np.array([0.0, 1.0, 0.5, 0.0], dtype=np.float64)
        ranges = np.array([1024.0, 2.0, 1.0, 1024.0], dtype=np.float64)
        gains = np.array([2.0, 1.0, 2.0, 0.0], dtype=np.float64)

        expected = np.array(
            [
                [4.0, 1.0, 25.0, 7.0],
                [5.0, 10.0, 250.0, 9.0]
            ],
            dtype=np.float64
        )

        actual = apply_preprocessing_numpy(events.copy(), decades, log0, ranges, gains)

        np.testing.assert_array_equal(actual, expected)

    @staticmethod
    def test_flowdata_apply_preprocessing_matches_as_array():
        flow_data = FlowData('data/fcs_files/B01 KC-A-W---91-US.fcs')

        actual = flow_data._apply_preprocessing(
            flow_data.as_array(preprocess=False).copy()
        )
        expected = flow_data.as_array(preprocess=True)

        np.testing.assert_array_equal(actual, expected)

    @unittest.skipUnless(
        HAS_PREPROCESSING_EXTENSION,
        "optional preprocessing extension unavailable"
    )
    @staticmethod
    def test_extension_matches_numpy_fallback():
        events = np.array(
            [
                [0.0, 16.0, 50.0, 7.0],
                [2.0, 32.0, 75.0, 9.0],
                [4.0, 48.0, 100.0, 11.0]
            ],
            dtype=np.float64
        )
        decades = np.array([0.0, 4.0, 5.0, 0.0], dtype=np.float64)
        log0 = np.array([0.0, 1.0, 0.1, 0.0], dtype=np.float64)
        ranges = np.array([1024.0, 256.0, 1024.0, 1024.0], dtype=np.float64)
        gains = np.array([2.0, 4.0, 1.5, 0.0], dtype=np.float64)

        expected = apply_preprocessing_numpy(
            events.copy(),
            decades,
            log0,
            ranges,
            gains
        )
        actual = _preprocessing_ext.apply_preprocessing(
            events.copy(),
            decades,
            log0,
            ranges,
            gains
        )

        np.testing.assert_allclose(actual, expected, rtol=0.0, atol=1e-12)
