"""
Utility for comparing FlowIO preprocessing backends on synthetic event data.

This is intended for local benchmarking only and is not part of the automated
test suite.
"""
import argparse
import timeit

import numpy as np

from flowio._preprocessing import (
    HAS_PREPROCESSING_EXTENSION,
    apply_preprocessing_numpy
)

if HAS_PREPROCESSING_EXTENSION:
    from flowio import _preprocessing_ext


def build_inputs(event_count, channel_count):
    rng = np.random.default_rng(0)
    events = rng.uniform(0.0, 1024.0, size=(event_count, channel_count))
    decades = np.linspace(0.0, 5.0, num=channel_count, dtype=np.float64)
    log0 = np.linspace(1.0, 0.1, num=channel_count, dtype=np.float64)
    ranges = np.full(channel_count, 1024.0, dtype=np.float64)
    gains = np.linspace(1.0, 4.0, num=channel_count, dtype=np.float64)

    gains[0] = 1.0
    decades[0] = 0.0

    return events, decades, log0, ranges, gains


def benchmark(label, func, events, decades, log0, ranges, gains, repeats, number):
    elapsed = min(
        timeit.repeat(
            lambda: func(
                events.copy(),
                decades,
                log0,
                ranges,
                gains
            ),
            repeat=repeats,
            number=number
        )
    )
    print(f"{label}: {elapsed:.6f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--events', type=int, default=50000)
    parser.add_argument('--channels', type=int, default=24)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--number', type=int, default=3)
    args = parser.parse_args()

    events, decades, log0, ranges, gains = build_inputs(
        args.events,
        args.channels
    )

    benchmark(
        'numpy-fallback',
        apply_preprocessing_numpy,
        events,
        decades,
        log0,
        ranges,
        gains,
        args.repeats,
        args.number
    )

    if HAS_PREPROCESSING_EXTENSION:
        benchmark(
            'c-extension',
            _preprocessing_ext.apply_preprocessing,
            events,
            decades,
            log0,
            ranges,
            gains,
            args.repeats,
            args.number
        )
    else:
        print('c-extension: unavailable')


if __name__ == '__main__':
    main()
