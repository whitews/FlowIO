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

    def test_create_fcs_data_offsets(self):
        """
        This tests whether FlowIO properly calculates
        byte offset locations for the FCS data section

        Create several small arrays of event data w/ only 1 channel.
        The array lengths are chosen to produce a file where the data section
        will end right before and after the 1000 byte offset location.
        These will be files 01 & 02

        Files 03 & 04 will have an extra metadata value for the keyword
        $COM (used for storing a comment) that will push the text section
        to a length that will make the data start byte location to be
        just below and above 1000.

        File 01:
          4-bytes per float value * 138 event values = 552 bytes
          header = 256 bytes
          text section = 192 bytes
          data start should be: 256 + 192 = 448
          data end should be: 448 + 552 - 1 = 999

        File 02:
          4-bytes per float value * 139 event values = 556 bytes
          header = 256 bytes
          text section (by default here) = 193 bytes
          data start should be: 256 + 193 = 449
          data end should be: 449 + 556 - 1 = 1004

        File 03:
          4-bytes per float value * 138 event values = 552 bytes
          header = 256 bytes
          extra text: 551
            4   bytes for '$COM'
            544 bytes ($COM value size)
            2   bytes (extra delimiters)
            1   byte (extra digit for data end location)
          text section  192 bytes (like File 01) + 551 (from above) = 743 bytes
          data start should be: 256 + 743 = 999
          data end should be: 999 + 552 - 1 = 1550

        File 04:
          4-bytes per float value * 138 event values = 552 bytes
          header = 256 bytes
          extra text: 553
            4   bytes for '$COM'
            545 bytes ($COM value size)
            2   bytes (extra delimiters)
            2   byte (extra digit for both data begin & data end location)
          text section  192 bytes (like File 01) + 553 (from above) = 745 bytes
          data start should be: 256 + 745 = 1001
          data end should be: 1001 + 552 - 1 = 1552
        """

        n_events_list = [138.0, 139.0]
        event_data_01 = list(np.arange(n_events_list[0]))
        event_data_02 = list(np.arange(n_events_list[1]))

        comment_value_01 = 'x' * 544
        comment_value_02 = 'x' * 545

        pnn_labels = ['FSC-A']

        export_file_path = "examples/fcs_files/test_fcs_export_data_offsets.fcs"

        # File 01
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data_01, channel_names=pnn_labels)
        fh.close()

        exported_flow_data_01 = FlowData(export_file_path)
        os.unlink(export_file_path)

        # File 02
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data_02, channel_names=pnn_labels)
        fh.close()

        exported_flow_data_02 = FlowData(export_file_path)
        os.unlink(export_file_path)

        # File 03
        fh = open(export_file_path, 'wb')
        metadata_dict = {'COM': comment_value_01}
        create_fcs(fh, event_data_01, channel_names=pnn_labels,  metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data_03 = FlowData(export_file_path)
        os.unlink(export_file_path)

        # File 04
        fh = open(export_file_path, 'wb')
        metadata_dict = {'COM': comment_value_02}
        create_fcs(fh, event_data_01, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data_04 = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertIsInstance(exported_flow_data_01, FlowData)
        self.assertListEqual(event_data_01, list(exported_flow_data_01.events))
        self.assertEqual(exported_flow_data_01.header['data_start'], 448)
        self.assertEqual(exported_flow_data_01.header['data_end'], 999)

        self.assertIsInstance(exported_flow_data_02, FlowData)
        self.assertListEqual(event_data_02, list(exported_flow_data_02.events))
        self.assertEqual(exported_flow_data_02.header['data_start'], 449)
        self.assertEqual(exported_flow_data_02.header['data_end'], 1004)

        self.assertIsInstance(exported_flow_data_03, FlowData)
        self.assertListEqual(event_data_01, list(exported_flow_data_03.events))
        self.assertEqual(exported_flow_data_03.header['data_start'], 999)
        self.assertEqual(exported_flow_data_03.header['data_end'], 1550)

        self.assertIsInstance(exported_flow_data_04, FlowData)
        self.assertListEqual(event_data_01, list(exported_flow_data_04.events))
        self.assertEqual(exported_flow_data_04.header['data_start'], 1001)
        self.assertEqual(exported_flow_data_04.header['data_end'], 1552)

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
