import unittest
import warnings
import array
from flowio import FlowData, read_multiple_data_sets
from flowio.exceptions import FCSParsingError


class FlowDataLMDTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.flow_data, self.fcs3_data = read_multiple_data_sets(
                'examples/fcs_files/coulter.lmd',
                ignore_offset_error=True
            )
        
    def test_event_count(self):
        self.assertEqual(
            len(self.flow_data.events) / self.flow_data.channel_count,
            int(self.flow_data.text['tot'])
        )

    def test_get_text(self):
        self.assertEqual(self.flow_data.text['cyt'], 'Cytomics FC 500')

    def test_fail_data_offset_error(self):
        with self.assertRaises(FCSParsingError):
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                FlowData('examples/fcs_files/coulter.lmd', nextdata_offset=0)

    def test_right_integer_reading(self):
        self.assertEqual(
            self.fcs3_data.events[:24], 
            array.array(
                "I",
                [
                    61056, 131840, 46, 324, 10309, 104, 11912, 0,
                    257280, 378656, 139, 1728, 58688, 354, 58720, 0,
                    164128, 305376, 159, 924, 29024, 208, 29728, 0
                ]
            )
        )
