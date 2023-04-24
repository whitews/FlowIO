import unittest
import warnings
from flowio import FlowData
from flowio.exceptions import FCSParsingError


class FlowDataLMDTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.flow_data = FlowData('examples/fcs_files/coulter.lmd', 
                                      ignore_offset_error=True,
                                      multiframe_offset=0,)
        
    def test_event_count(self):
        self.assertEqual(
            len(self.flow_data.events) / self.flow_data.channel_count,
            int(self.flow_data.text['tot'])
        )

    def test_get_text(self):
        self.assertEqual(self.flow_data.text['cyt'], 'Cytomics FC 500')

    def test_fail_data_offset_error(self):
        with self.assertRaises(FCSParsingError):     
            FlowData('examples/fcs_files/coulter.lmd', multiframe_offset=0)
