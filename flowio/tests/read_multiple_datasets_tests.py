import unittest
from flowio.exceptions import MultipleFramesDetectedError
from flowio.flowdata import FlowData
from flowio.utility import read_multiple_flowframes

class MultipleDatasetsTestCase(unittest.TestCase):
    def setUp(self):
        self.file = "examples/fcs_files/coulter.lmd"
        self.amount_datasets = 2
        self.channel_count = 8
        self.event_count = 18110

    def test_raise_error(self):
        with self.assertRaises(MultipleFramesDetectedError):
            FlowData(self.file)

    def test_read_multiple_flowframes(self):
        frames = read_multiple_flowframes(self.file, ignore_offset_error=True)

        self.assertEqual(len(frames), 2)
        self.assertIsInstance(frames[0], FlowData)
        self.assertIsInstance(frames[1], FlowData)

        self.assertEqual(frames[0].header["version"], "2.0")
        self.assertEqual(frames[1].header["version"], "3.0")

        self.assertEqual(frames[0].channel_count, self.channel_count)
        self.assertEqual(frames[1].channel_count, self.channel_count)

        self.assertEqual(frames[0].event_count, self.event_count)
        self.assertEqual(frames[1].event_count, self.event_count)


