import unittest
from flowio import FlowData


class FlowDataLMDTestCase(unittest.TestCase):
    def setUp(self):
        self.flowdata = FlowData('sample_data/coulter.lmd')
        
    def test_get_points(self):
        self.assertEqual(
            len(self.flowdata.events)/self.flowdata.channel_count,
            int(self.flowdata.text['tot']))

    def test_get_text(self):
        self.assertEqual(self.flowdata.text['cyt'], 'Cytomics FC 500')

if __name__ == '__main__':
    suite1 = unittest.makeSuite(FlowDataLMDTestCase, 'test')
    unittest.main()