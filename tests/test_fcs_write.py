import unittest
import os
import numpy as np
import warnings
from flowio import FlowData, create_fcs
from flowio.fcs_keywords import FCS_STANDARD_KEYWORDS
from flowio.exceptions import PnEWarning


class CreateFCSTestCase(unittest.TestCase):
    def setUp(self):
        self.flow_data = FlowData('examples/fcs_files/100715.fcs')

    def test_create_fcs(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

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
        just below and above 1000. Both 03 & 04 use the data events from
        file 01 (540 bytes)

        File 01:
          4-bytes per float value * 135 event values = 540 bytes
          header = 256 bytes
          text section = 201 bytes
          data start should be: 256 + 201 = 457
          data end should be: 457 + 540 - 1 = 996

        File 02:
          4-bytes per float value * 136 event values = 544 bytes
          header = 256 bytes
          text section (by default here) = 202 bytes
          data start should be: 256 + 202 = 458
          data end should be: 458 + 544 - 1 = 1001

        File 03:
          4-bytes per float value * 135 event values = 540 bytes
          header = 256 bytes
          extra text: 542
            4   bytes for '$COM'
            535 bytes ($COM value size)
            2   bytes (extra delimiters)
            1   byte (extra digit for data end location)
          text section  201 bytes (like File 01) + 542 (from above) = 743 bytes
          data start should be: 256 + 743 = 999
          data end should be: 999 + 540 - 1 = 1538

        File 04:
          4-bytes per float value * 136 event values = 540 bytes
          header = 256 bytes
          extra text: 544
            4   bytes for '$COM'
            536 bytes ($COM value size)
            2   bytes (extra delimiters)
            2   byte (extra digit for both data begin & data end location)
          text section  201 bytes (like File 01) + 544 (from above) = 745 bytes
          data start should be: 256 + 745 = 1001
          data end should be: 1001 + 540 - 1 = 1540
        """

        n_events_list = [135.0, 136.0]
        event_data_01 = list(np.arange(n_events_list[0]))
        event_data_02 = list(np.arange(n_events_list[1]))

        comment_value_01 = 'x' * 535
        comment_value_02 = 'x' * 536

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
        self.assertEqual(exported_flow_data_01.header['data_start'], 457)
        self.assertEqual(exported_flow_data_01.header['data_stop'], 996)

        self.assertIsInstance(exported_flow_data_02, FlowData)
        self.assertListEqual(event_data_02, list(exported_flow_data_02.events))
        self.assertEqual(exported_flow_data_02.header['data_start'], 458)
        self.assertEqual(exported_flow_data_02.header['data_stop'], 1001)

        self.assertIsInstance(exported_flow_data_03, FlowData)
        self.assertListEqual(event_data_01, list(exported_flow_data_03.events))
        self.assertEqual(exported_flow_data_03.header['data_start'], 999)
        self.assertEqual(exported_flow_data_03.header['data_stop'], 1538)

        self.assertIsInstance(exported_flow_data_04, FlowData)
        self.assertListEqual(event_data_01, list(exported_flow_data_04.events))
        self.assertEqual(exported_flow_data_04.header['data_start'], 1001)
        self.assertEqual(exported_flow_data_04.header['data_stop'], 1540)

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
        self.assertEqual(exported_flow_data.header['data_stop'], 0)
        self.assertGreater(int(exported_flow_data.text['enddata']), 99999999)

    def test_create_fcs_with_opt_channel_labels(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]
        pns_labels = [v['pns'] for k, v in channel_names.items()]

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
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

        metadata_dict = {}

        for k, v in self.flow_data.text.items():
            if k in FCS_STANDARD_KEYWORDS:
                metadata_dict[k] = v

        metadata_dict['$P1D'] = 'Linear,0,10'
        metadata_dict['$P1F'] = '520LP'
        metadata_dict['$P1L'] = '588'
        metadata_dict['$P1O'] = '200'
        metadata_dict['$P1P'] = '50'
        metadata_dict['$P1T'] = 'PMT9524'
        metadata_dict['$P1V'] = '250'
        metadata_dict['$VOL'] = '120'
        metadata_dict['$P1CALIBRATION'] = '1.234,MESF'

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"
        fh = open(export_file_path, 'wb')
        create_fcs(fh, event_data, channel_names=pnn_labels, metadata_dict=metadata_dict)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(exported_flow_data.text['cyt'], 'Main Aria (FACSAria)')
        self.assertEqual(exported_flow_data.text['p1d'], 'Linear,0,10')
        self.assertEqual(exported_flow_data.text['p1f'], '520LP')
        self.assertEqual(exported_flow_data.text['p1l'], '588')
        self.assertEqual(exported_flow_data.text['p1o'], '200')
        self.assertEqual(exported_flow_data.text['p1p'], '50')
        self.assertEqual(exported_flow_data.text['p1t'], 'PMT9524')
        self.assertEqual(exported_flow_data.text['p1v'], '250')
        self.assertEqual(exported_flow_data.text['vol'], '120')
        self.assertEqual(exported_flow_data.text['p1calibration'], '1.234,MESF')

    def test_create_fcs_with_non_std_metadata(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

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
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

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

    def test_create_fcs_with_log_pne_warns(self):
        event_data = self.flow_data.events
        channel_names = self.flow_data.channels
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

        metadata_dict = {
            'p9e': '4,1'
        }

        export_file_path = "examples/fcs_files/test_fcs_export.fcs"

        with open(export_file_path, 'wb') as fh:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                self.assertWarns(
                    PnEWarning,
                    create_fcs,
                    fh,
                    event_data,
                    channel_names=pnn_labels,
                    opt_channel_names=None,
                    metadata_dict=metadata_dict
                )

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
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

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
        pnn_labels = [v['pnn'] for k, v in channel_names.items()]

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
        pnn_labels = [v['pnn'] for k, v in flow_data.channels.items()]

        metadata = flow_data.text.copy()

        # FlowIO doesn't currently support writing files with non-float data types
        metadata['datatype'] = 'F'

        fh = open(export_file_path, 'wb')
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            create_fcs(fh, flow_data.events, pnn_labels, metadata_dict=metadata)
        fh.close()

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertEqual(flow_data.events[0], exported_flow_data.events[0])

    def test_create_and_read_empty_fcs(self):
        event_data = []
        pnn_labels = [v["pnn"] for k, v in self.flow_data.channels.items()]
        pns_labels = [v["pns"] for k, v in self.flow_data.channels.items()]

        metadata_dict = {"p9g": "2"}

        export_file_path = "examples/fcs_files/test_fcs_export_empty.fcs"
        with open(export_file_path, "wb") as export_file:
            create_fcs(
                export_file,
                event_data,
                channel_names=pnn_labels,
                opt_channel_names=pns_labels,
                metadata_dict=metadata_dict,
            )

        exported_flow_data = FlowData(export_file_path)
        os.unlink(export_file_path)

        self.assertIsInstance(exported_flow_data, FlowData)
        self.assertEqual(len(exported_flow_data.events), 0)
        self.assertEqual(exported_flow_data.pnn_labels, self.flow_data.pnn_labels)
        self.assertEqual(exported_flow_data.pns_labels, self.flow_data.pns_labels)
        self.assertEqual(exported_flow_data.text["p9g"], "2")
