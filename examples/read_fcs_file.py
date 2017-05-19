import flowio

fd = flowio.FlowData('data_set1.fcs')

print(len(fd.events))
print(fd.text)