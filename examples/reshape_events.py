import flowio
import numpy

f = flowio.FlowData('001_F6901PRY_21_C1_C01.fcs')
n = numpy.reshape(f.events, (-1, f.channel_count))
