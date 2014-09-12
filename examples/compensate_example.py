import flowio
import flowutils
import numpy

fd = flowio.FlowData('example.fcs')
spill, markers = flowutils.compensate.get_spill(fd.text['spill'])
events = numpy.reshape(fd.events, (-1, fd.channel_count))

fluoro_indices = []

for channel in fd.channels:
    if fd.channels[channel]['PnN'] in markers:
        fluoro_indices.append(int(channel) - 1)

comp_events = flowutils.compensate.compensate(
    events,
    spill,
    fluoro_indices
)

print 'Events shape: ' + str(events.shape)
print 'Comp Events shape: ' + str(comp_events.shape)

print events[:2]

print comp_events[:2]


