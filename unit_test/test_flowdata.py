import unittest
import io
from flowio import FlowData


class FlowDataTestCase(unittest.TestCase):
    def setUp(self):
        self.flowdata = FlowData('sample_data/3FITC_4PE_004.fcs')
        
    def test_get_points(self):
        self.assertEqual(
            len(self.flowdata.events)/self.flowdata.channel_count,
            int(self.flowdata.text['tot']))

    def test_get_text(self):
        self.assertEqual(self.flowdata.text['cyt'], 'FACScan')
        
    @staticmethod
    def test_load_fcs():
        for unused in range(100):
            FlowData('sample_data/3FITC_4PE_004.fcs')

    @staticmethod
    def test_load_fcs_from_memory():
        with open('sample_data/3FITC_4PE_004.fcs') as f:
            mem_file = io.BytesIO(f.read())
            FlowData(mem_file)

if __name__ == '__main__':
    suite1 = unittest.makeSuite(FlowDataTestCase, 'test')
    unittest.main()