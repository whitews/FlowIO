import unittest

import numpy as np
from flowio import FlowData
from flowio.exceptions import UnsupportedLazyDataError


class LazyDataAccessTestCase(unittest.TestCase):
    float_fcs = 'data/fcs_files/G11.fcs'
    int_fcs = 'data/fcs_files/3FITC_4PE_004.fcs'
    var_int_fcs = 'data/fcs_files/variable_int_example.fcs'
    be_float_fcs = 'data/fcs_files/100715.fcs'

    def test_only_text_exposes_data_offsets(self):
        meta = FlowData(self.float_fcs, only_text=True)
        full = FlowData(self.float_fcs)

        self.assertIsNone(meta.events)
        self.assertEqual(meta.data_start, full.data_start)
        self.assertEqual(meta.data_stop, full.data_stop)
        self.assertEqual(meta.data_byte_range, full.data_byte_range)
        self.assertEqual(meta.event_count, full.event_count)
        self.assertEqual(meta.channel_count, full.channel_count)
        self.assertEqual(meta.data_type, 'F')

    def test_as_memmap_matches_full_load(self):
        meta = FlowData(self.float_fcs, only_text=True)
        full = FlowData(self.float_fcs)
        truth = full.as_array(preprocess=False)

        mmap_view = meta.as_memmap()
        self.assertEqual(mmap_view.shape, (meta.event_count, meta.channel_count))
        self.assertFalse(mmap_view.flags.writeable)
        np.testing.assert_array_equal(np.asarray(mmap_view, dtype=np.float64), truth)

    def test_as_memmap_big_endian_float(self):
        meta = FlowData(self.be_float_fcs, only_text=True)
        full = FlowData(self.be_float_fcs)
        truth = full.as_array(preprocess=False)

        mmap_view = meta.as_memmap()
        self.assertEqual(str(mmap_view.dtype), '>f4')
        np.testing.assert_array_equal(np.asarray(mmap_view, dtype=np.float64), truth)

    def test_read_events_from_only_text(self):
        meta = FlowData(self.float_fcs, only_text=True)
        full = FlowData(self.float_fcs)
        truth = full.as_array(preprocess=False)
        indices = [0, 1, 10, meta.event_count - 1]

        rows = meta.read_events(indices=indices, preprocess=False)
        self.assertEqual(rows.shape, (len(indices), meta.channel_count))
        self.assertEqual(rows.dtype, np.float64)
        np.testing.assert_array_equal(rows, truth[indices])

        all_rows = meta.read_events(preprocess=False)
        np.testing.assert_array_equal(all_rows, truth)

    def test_read_events_preprocess_default_matches_as_array(self):
        meta = FlowData(self.float_fcs, only_text=True)
        full = FlowData(self.float_fcs)
        truth = full.as_array(preprocess=True)

        all_rows = meta.read_events()
        np.testing.assert_array_equal(all_rows, truth)

        rows = meta.read_events(indices=[0, 10, 100])
        np.testing.assert_array_equal(rows, truth[[0, 10, 100]])

    def test_read_events_from_loaded_integer_file(self):
        full = FlowData(self.int_fcs)
        truth = full.as_array(preprocess=False)
        indices = [0, 5, 100]

        rows = full.read_events(indices=indices, preprocess=False)
        np.testing.assert_array_equal(rows, truth[indices])

    def test_numpy_dtype_and_byte_range(self):
        meta = FlowData(self.float_fcs, only_text=True)
        dtype = meta.numpy_dtype()
        self.assertEqual(dtype, np.dtype('<f4'))

        start, stop = meta.data_byte_range
        self.assertEqual(start, meta.data_start)
        self.assertEqual(stop, meta.data_stop)
        expected_bytes = meta.event_count * meta.channel_count * dtype.itemsize
        self.assertEqual(stop - start + 1, expected_bytes)

    def test_as_memmap_rejects_integer_datatype(self):
        meta = FlowData(self.int_fcs, only_text=True)
        with self.assertRaises(UnsupportedLazyDataError):
            meta.numpy_dtype()
        with self.assertRaises(UnsupportedLazyDataError):
            meta.as_memmap()
        with self.assertRaises(UnsupportedLazyDataError):
            meta.read_events(indices=[0])

    def test_as_memmap_rejects_variable_bit_width(self):
        meta = FlowData(self.var_int_fcs, only_text=True)
        with self.assertRaises(UnsupportedLazyDataError):
            meta.as_memmap()

    def test_as_memmap_rejects_in_memory_file(self):
        with open(self.float_fcs, 'rb') as fh:
            data = fh.read()
        import io
        mem = io.BytesIO(data)
        meta = FlowData(mem, only_text=True)
        with self.assertRaises(UnsupportedLazyDataError):
            meta.as_memmap()

    def test_as_array_still_requires_events(self):
        meta = FlowData(self.float_fcs, only_text=True)
        with self.assertRaises(AttributeError):
            meta.as_array()
