import unittest
import os
import numpy as np
from flowio import FlowData, create_fcs
from flowio.fcs_keywords import FCS_STANDARD_KEYWORDS


class CreateFCSTestCase(unittest.TestCase):
    def setUp(self):
        self.flow_data = FlowData('examples/fcs_files/100715.fcs')

    def test_create_fcs(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertIsInstance(exported_flow_data, FlowData)

    def test_create_large_fcs(self):
        # create 100,000,000 bytes of event data
        # 4-bytes per float value * 4 channels * 6,250,000 events
        n_events = 6250000
        n_channels = 4
        np.random.seed(1)
        event_data = np.random.random(n_channels * n_events).tolist()

        pnn_labels = [
            'FSC-A',
            'SSC-A',
            'FLR1-A',
            'FLR2-A'
        ]

        export_file_path = "examples/fcs_files/test_large_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertIsInstance(exported_flow_data, FlowData)
        self.assertEqual(exported_flow_data.header['data_start'], 0)
        self.assertEqual(exported_flow_data.header['data_end'], 0)
        self.assertGreater(int(exported_flow_data.text['enddata']), 99999999)

    def test_create_fcs_with_opt_channel_labels(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]
        pns_labels = [v['PnS'] for k, v in channel_names.items()]

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, opt_channel_names=pns_labels)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        p5s_label_truth = 'CD3'
        p5s_label_value = exported_flow_data.text['p5s']

        self.assertEqual(p5s_label_value, p5s_label_truth)

    def test_create_fcs_with_std_metadata(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {}

        for k, v in self.flow_data.text.items():
            if k in FCS_STANDARD_KEYWORDS:
                metadata_dict[k] = v

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        cyt_truth = 'Main Aria (FACSAria)'
        cyt_value = exported_flow_data.text['cyt']

        self.assertEqual(cyt_value, cyt_truth)

    def test_create_fcs_with_non_std_metadata(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'custom_tag': 'added by flowio',
            'cyt': 'Main Aria (FACSAria)'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        custom_tag_truth = 'added by flowio'
        custom_tag_value = exported_flow_data.text['custom_tag']

        last_key_truth = 'custom_tag'
        last_key_actual = list(exported_flow_data.text.keys())[-1]

        self.assertEqual(last_key_actual, last_key_truth)
        self.assertEqual(custom_tag_value, custom_tag_truth)

    def test_create_fcs_with_png(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9g': '2',
            'p11g': '2'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(exported_flow_data.text['p9g'], '2')

    def test_create_fcs_with_log_pne(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9e': '4,1'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')

        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)

        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(exported_flow_data.text['p9e'], '4,1')

    def test_create_fcs_with_log0_pne(self):
        """
        This tests using the invalid PnE log0 value of 0.
        Unfortunately, this is commonly found in files, and
        FCS 3.1 states to treat it as a 1. create_fcs will
        do this automatically if given decades > 0 and
        log0 == 0
        """
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9e': '4,0'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')

        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)

        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(exported_flow_data.text['p9e'], '4,1')

    def test_create_fcs_with_invalid_gain_with_log_pne(self):
        """
        This tests using the invalid combination of a log
        scaling PnE value & gain value != 1.
        """
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9e': '4,1',
            'p9g': '2'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')

        self.assertRaises(
            ValueError,
            create_fcs,
            fh,
            event_data,
            channel_names=pnn_labels,
            metadata_dict=metadata_dict
        )

        fh.close()
        os.unlink(export_file_path)

    def test_create_fcs_with_pnr(self):
        """
        This tests using the invalid PnE log0 value of 0.
        Unfortunately, this is commonly found in files, and
        FCS 3.1 states to treat it as a 1. create_fcs will
        do this automatically if given decades > 0 and
        log0 == 0
        """
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9r': '2048'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')

        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)

        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(exported_flow_data.text['p9r'], '2048')

    def test_create_fcs_ignore_extra_pnn(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['PnN'] for k, v in channel_names.items()]

        # this p9n value should get ignored
        metadata_dict = {
            'p9n': 'FLR1-A'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        p9n_tag_truth = 'V655-A'
        p9n_tag_value = exported_flow_data.text['p9n']

        self.assertEqual(p9n_tag_value, p9n_tag_truth)

    def test_create_fcs_with_2byte_char(self):
        fcs_path = "examples/fcs_files/data1.fcs"
        export_file_path = "examples/fcs_files/test_fcs_export.fcs"

        flow_data = FlowData(fcs_path)
        pnn_labels = [v['PnN'] for k, v in flow_data.channels.items()]

        metadata = flow_data.text.copy()

        fh = open(export_file_path, 'wb')
        create_fcs(fh, flow_data.events, pnn_labels, metadata_dict=metadata)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(flow_data.events[0], exported_flow_data.events[0])
