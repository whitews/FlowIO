import flowio
import numpy

f = flowio.FlowData('fcs_files/data1.fcs')
n = numpy.reshape(f.events, (-1, f.channel_count))

print(n.shape)
