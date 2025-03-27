import flowio
import flowutils

fd = flowio.FlowData('fcs_files/100715.fcs')
spill, markers = flowutils.compensate.get_spill(fd.text['spill'])
events = fd.as_array()

fluoro_indices = []

for channel in fd.channels:
    if fd.channels[channel]['pnn'] in markers:
        fluoro_indices.append(int(channel) - 1)

fluoro_indices.sort()

comp_events = flowutils.compensate.compensate(
    events,
    spill,
    fluoro_indices
)

print('Events shape: ' + str(events.shape))
print('Comp Events shape: ' + str(comp_events.shape))

print(events[:1])

print(comp_events[:1])
