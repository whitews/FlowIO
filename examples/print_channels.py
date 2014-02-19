import flowio
import os
import sys

if len(sys.argv) > 1:
    flow_dir = sys.argv[1]
else:
    flow_dir = os.getcwd()

files = os.listdir(flow_dir)

for file in files:
    try:
        flow_data = flowio.FlowData("/".join([flow_dir,file]))
    except:
        continue

    print file + ':'
    for key in sorted(flow_data.channels.keys()):
        line = key + '\t' + \
            flow_data.channels[key]['PnN'] + '\t'
        if 'PnS' in flow_data.channels[key]:
            line += flow_data.channels[key]['PnS']

        print '\t' + line

    if 'creator' in flow_data.text:
        print '\t' + 'Creator: ' + flow_data.text['creator']
    if 'export time' in flow_data.text:
        print '\t' + 'Export time: ' + flow_data.text['export time']
    if 'experiment name' in flow_data.text:
        print '\t' + 'Experiment name: ' + flow_data.text['experiment name']
    if 'patient id' in flow_data.text:
        print '\t' + 'Patient ID: ' + flow_data.text['patient id']
    if 'tube name' in flow_data.text:
        print '\t' + 'Tube name: ' + flow_data.text['tube name']
    if 'src' in flow_data.text:
        print '\t' + 'Source: ' + flow_data.text['src']
    if 'sample id' in flow_data.text:
        print '\t' + 'Sample ID: ' + flow_data.text['sample id']
    if 'tot' in flow_data.text:
        print '\t' + 'Total: ' + flow_data.text['tot']