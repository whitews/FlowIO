import unittest
import os
from flowio import FlowData, create_fcs


class CreateFCSTestCase(unittest.TestCase):
    def setUp(self):
        self.flow_data = FlowData('examples/fcs_files/100715.fcs')

    def test_create_fcs(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(event_data, channel_names=pnn_labels, file_handle=fh)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertIsInstance(exported_flow_data, FlowData)