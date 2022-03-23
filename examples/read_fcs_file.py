import flowio

fd = flowio.FlowData('fcs_files/data1.fcs')

print(len(fd.events))
print(fd.text)
