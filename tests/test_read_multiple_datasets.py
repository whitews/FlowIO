import unittest
import warnings
from flowio.exceptions import MultipleDataSetsError
from flowio.flowdata import FlowData
from flowio.utils import read_multiple_data_sets


class MultipleDatasetsTestCase(unittest.TestCase):
    def setUp(self):
        self.file = "examples/fcs_files/coulter.lmd"
        self.amount_datasets = 2
        self.channel_count = 8
        self.event_count = 18110

    def test_raise_error(self):
        with self.assertRaises(MultipleDataSetsError):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                FlowData(self.file)

    def test_read_multiple_data_sets(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            fd_data_sets = read_multiple_data_sets(self.file, ignore_offset_error=True)

        self.assertEqual(len(fd_data_sets), 2)
        self.assertIsInstance(fd_data_sets[0], FlowData)
        self.assertIsInstance(fd_data_sets[1], FlowData)

        self.assertEqual(fd_data_sets[0].header["version"], "2.0")
        self.assertEqual(fd_data_sets[1].header["version"], "3.0")

        self.assertEqual(fd_data_sets[0].channel_count, self.channel_count)
        self.assertEqual(fd_data_sets[1].channel_count, self.channel_count)

        self.assertEqual(fd_data_sets[0].event_count, self.event_count)
        self.assertEqual(fd_data_sets[1].event_count, self.event_count)
