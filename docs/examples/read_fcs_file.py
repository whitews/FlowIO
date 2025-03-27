import flowio

fd = flowio.FlowData('../../data/fcs_files/data1.fcs')

print(len(fd.events))
print(fd.text)
