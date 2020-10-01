import unittest
import io
from flowio import FlowData


class FlowDataTestCase(unittest.TestCase):
    def setUp(self):
        self.flow_data = FlowData('examples/fcs_files/3FITC_4PE_004.fcs')
        
    def test_get_points(self):
        self.assertEqual(
            len(self.flow_data.events) / self.flow_data.channel_count,
            int(self.flow_data.text['tot']))

    def test_get_text(self):
        self.assertEqual(self.flow_data.text['cyt'], 'FACScan')

    @staticmethod
    def test_load_fcs_from_memory():
        with open('examples/fcs_files/3FITC_4PE_004.fcs', 'rb') as f:
            mem_file = io.BytesIO(f.read())
            FlowData(mem_file)

    def test_issue_03(self):
        """
        Tests Attune FCS files for error in FlowData method parse_float_data:

        flowio/flowdata.py in __parse_float_data(self, offset, start, stop, data_type, order)
            256
            257         tmp = unpack('%s%d%s' % (order, num_items, data_type),
        --> 258                      self.__read_bytes(offset, start, stop))
            259         return tmp
            260

        error: unpack requires a buffer of 277676 bytes
        """
        flow_data = FlowData('examples/fcs_files/G11.fcs')

        self.assertIsInstance(flow_data, FlowData)
