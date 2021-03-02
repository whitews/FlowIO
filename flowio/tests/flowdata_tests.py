import shutil
import unittest
import os
import io
import tempfile
from flowio import FlowData


class FlowDataTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.flow_data = FlowData('examples/fcs_files/3FITC_4PE_004.fcs')
        self.flow_data_spill = FlowData('examples/fcs_files/100715.fcs')

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

    def test_load_temp_file(self):
        with tempfile.TemporaryFile() as tmpfile:
            with open('examples/fcs_files/3FITC_4PE_004.fcs', 'r+b') as f:
                shutil.copyfileobj(f, tmpfile)
            tmpfile.seek(0)
            out_data = FlowData(tmpfile)

    def test_load_non_file_input(self):
        non_file = object()
        self.assertRaises(AttributeError, FlowData, non_file)

    def test_write_fcs(self):
        file_name = 'flowio/tests/flowio_test_write_fcs.fcs'
        self.flow_data_spill.write_fcs(file_name)

        fcs_export = FlowData(file_name)

        self.assertIsInstance(fcs_export, FlowData)
        os.unlink(file_name)

    def test_write_fcs_preserves_channels(self):
        orig_fd = FlowData('examples/fcs_files/100715.fcs')
        expected = orig_fd.channels

        with tempfile.NamedTemporaryFile() as tmpfile:
            orig_fd.write_fcs(tmpfile.name)
            out_data = FlowData(tmpfile.name)
            actually = out_data.channels

            self.assertDictEqual(expected, actually)

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
